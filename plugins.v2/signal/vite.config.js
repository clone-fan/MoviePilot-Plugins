import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

function collectScriptScopeIds(code) {
  return [...code.matchAll(/['"]__scopeId['"]\s*,\s*["']([^"']+)["']/g)].map(match => match[1])
}

function collectCssScopeIds(source) {
  return [...source.matchAll(/\[(data-v-[^\]]+)\]/g)].map(match => match[1])
}

function collectLocalScriptImports(code) {
  return [
    ...code.matchAll(/(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?['"]\.\/([^'"]+\.js)['"]/g),
    ...code.matchAll(/import\(['"]\.\/([^'"]+\.js)['"]\)/g),
  ].map(match => match[1])
}

function findBundleItem(bundle, fileName) {
  return (
    bundle[fileName] ||
    bundle[`assets/${fileName}`] ||
    Object.values(bundle).find(item => item.fileName === fileName || item.fileName.endsWith(`/${fileName}`))
  )
}

function parseRemoteExposeEntries(remoteCode) {
  return [
    ...remoteCode.matchAll(/dynamicLoadingCss\(\[([^\]]*)\][\s\S]*?__federation_import\('\.\/([^']+\.js)'\)/g),
  ].map(([, cssList, jsFile]) => ({
    cssFiles: [...cssList.matchAll(/["']([^"']+\.css)["']/g)].map(match => match[1]),
    jsFile,
  })).filter(entry => entry.cssFiles.length && entry.jsFile)
}

function collectBundleScriptScopes(bundle, fileName, seen = new Set()) {
  if (seen.has(fileName)) return []
  seen.add(fileName)

  const chunk = findBundleItem(bundle, fileName)
  if (chunk?.type !== 'chunk') return []

  const scopes = collectScriptScopeIds(chunk.code)
  for (const importFile of collectLocalScriptImports(chunk.code)) {
    scopes.push(...collectBundleScriptScopes(bundle, importFile, seen))
  }
  return [...new Set(scopes)]
}

function collectFileScriptScopes(outputDir, remoteDir, fileName, seen = new Set()) {
  if (seen.has(fileName)) return []
  seen.add(fileName)

  const source = readFileSync(join(outputDir, remoteDir, fileName), 'utf8')
  const scopes = collectScriptScopeIds(source)
  for (const importFile of collectLocalScriptImports(source)) {
    scopes.push(...collectFileScriptScopes(outputDir, remoteDir, importFile, seen))
  }
  return [...new Set(scopes)]
}

function replaceMissingCssScopes(cssSources, jsScopes, label) {
  const cssScopes = [...new Set(cssSources.flatMap(source => collectCssScopeIds(source)))]
  const missingScopes = jsScopes.filter(scope => !cssScopes.includes(scope))
  const extraScopes = cssScopes.filter(scope => !jsScopes.includes(scope))

  if (!missingScopes.length) return cssSources

  if (missingScopes.length !== extraScopes.length) {
    throw new Error(
      `Unable to sync federation CSS scopes for ${label}: missing ${missingScopes.join(', ')}; extra ${extraScopes.join(', ')}`,
    )
  }

  return cssSources.map(source => {
    let next = source
    for (let index = 0; index < missingScopes.length; index += 1) {
      next = next.split(extraScopes[index]).join(missingScopes[index])
    }
    return next
  })
}

function syncFederationScopedCss() {
  return {
    name: 'signal-sync-federation-scoped-css',
    generateBundle(_, bundle) {
      const remoteEntry = Object.values(bundle).find(item => item.fileName?.endsWith('remoteEntry.js'))
      const remoteCode = remoteEntry?.type === 'chunk'
        ? remoteEntry.code
        : remoteEntry?.type === 'asset'
          ? String(remoteEntry.source)
          : ''

      for (const { cssFiles, jsFile } of parseRemoteExposeEntries(remoteCode)) {
        const cssAssets = cssFiles
          .map(cssFile => findBundleItem(bundle, cssFile))
          .filter(asset => asset?.type === 'asset')
        if (cssAssets.length !== cssFiles.length) continue

        const cssSources = cssAssets.map(asset => (
          typeof asset.source === 'string'
            ? asset.source
            : Buffer.from(asset.source).toString('utf8')
        ))
        const jsScopes = collectBundleScriptScopes(bundle, jsFile)
        const nextSources = replaceMissingCssScopes(cssSources, jsScopes, jsFile)

        nextSources.forEach((source, index) => {
          cssAssets[index].source = source
        })
      }
    },
    writeBundle(options, bundle) {
      const remoteEntry = Object.values(bundle).find(item => item.fileName?.endsWith('remoteEntry.js'))
      if (!remoteEntry?.fileName) return

      const outputDir = options.dir || 'dist'
      const remoteDir = dirname(remoteEntry.fileName)
      const remotePath = join(outputDir, remoteEntry.fileName)
      const remoteCode = readFileSync(remotePath, 'utf8')

      for (const { cssFiles, jsFile } of parseRemoteExposeEntries(remoteCode)) {
        const cssPaths = cssFiles.map(cssFile => join(outputDir, remoteDir, cssFile))
        const cssSources = cssPaths.map(cssPath => readFileSync(cssPath, 'utf8'))
        const jsScopes = collectFileScriptScopes(outputDir, remoteDir, jsFile)
        const nextSources = replaceMissingCssScopes(cssSources, jsScopes, jsFile)

        nextSources.forEach((source, index) => {
          if (source !== cssSources[index]) writeFileSync(cssPaths[index], source)
        })
      }
    },
  }
}

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'Signal',
      filename: 'remoteEntry.js',
      exposes: {
        './Config': './src/app/Config.vue',
        './AppPageConfig': './src/app/AppPageConfig.vue',
        './Page': './src/app/Page.vue',
        './Dashboard': './src/app/Dashboard.vue',
      },
      shared: {
        vue: {
          requiredVersion: false,
          generate: false,
        },
      },
      format: 'esm',
    }),
    syncFederationScopedCss(),
  ],
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: true,
  },
  css: {
    postcss: {
      plugins: [
        {
          postcssPlugin: 'internal:charset-removal',
          AtRule: {
            charset: atRule => {
              if (atRule.name === 'charset') atRule.remove()
            },
          },
        },
        {
          postcssPlugin: 'vuetify-filter',
          Root(root) {
            root.walkRules(rule => {
              if (rule.selector && (rule.selector.includes('.v-') || rule.selector.includes('.mdi-'))) {
                rule.remove()
              }
            })
          },
        },
      ],
    },
  },
})
