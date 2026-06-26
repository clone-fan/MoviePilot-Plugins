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

function findBundleItem(bundle, fileName) {
  return (
    bundle[fileName] ||
    bundle[`assets/${fileName}`] ||
    Object.values(bundle).find(item => item.fileName === fileName || item.fileName.endsWith(`/${fileName}`))
  )
}

function syncFederationScopedCss() {
  return {
    name: 'agentops-sync-federation-scoped-css',
    generateBundle(_, bundle) {
      const remoteEntry = Object.values(bundle).find(item => item.fileName?.endsWith('remoteEntry.js'))
      const remoteCode = remoteEntry?.type === 'chunk'
        ? remoteEntry.code
        : remoteEntry?.type === 'asset'
          ? String(remoteEntry.source)
          : ''
      const exposedPairs = [
        ...remoteCode.matchAll(/dynamicLoadingCss\(\["([^"]+\.css)"\][\s\S]*?__federation_import\('\.\/([^']+\.js)'\)/g),
      ]

      for (const [, cssFile, jsFile] of exposedPairs) {
        const cssAsset = findBundleItem(bundle, cssFile)
        const jsChunk = findBundleItem(bundle, jsFile)
        if (cssAsset?.type !== 'asset' || jsChunk?.type !== 'chunk') continue

        let cssSource = typeof cssAsset.source === 'string'
          ? cssAsset.source
          : Buffer.from(cssAsset.source).toString('utf8')
        const jsScopes = [...new Set(collectScriptScopeIds(jsChunk.code))]
        const cssScopes = [...new Set(collectCssScopeIds(cssSource))]
        const missingScopes = jsScopes.filter(scope => !cssScopes.includes(scope))
        const extraScopes = cssScopes.filter(scope => !jsScopes.includes(scope))

        if (!missingScopes.length || missingScopes.length !== extraScopes.length) continue

        for (let index = 0; index < missingScopes.length; index += 1) {
          cssSource = cssSource.split(extraScopes[index]).join(missingScopes[index])
        }
        cssAsset.source = cssSource
      }
    },
    writeBundle(options, bundle) {
      const remoteEntry = Object.values(bundle).find(item => item.fileName?.endsWith('remoteEntry.js'))
      if (!remoteEntry?.fileName) return

      const outputDir = options.dir || 'dist'
      const remoteDir = dirname(remoteEntry.fileName)
      const remotePath = join(outputDir, remoteEntry.fileName)
      const remoteCode = readFileSync(remotePath, 'utf8')
      const exposedPairs = [
        ...remoteCode.matchAll(/dynamicLoadingCss\(\["([^"]+\.css)"\][\s\S]*?__federation_import\('\.\/([^']+\.js)'\)/g),
      ]

      for (const [, cssFile, jsFile] of exposedPairs) {
        const cssPath = join(outputDir, remoteDir, cssFile)
        const jsPath = join(outputDir, remoteDir, jsFile)
        let cssSource = readFileSync(cssPath, 'utf8')
        const jsSource = readFileSync(jsPath, 'utf8')
        const jsScopes = [...new Set(collectScriptScopeIds(jsSource))]
        const cssScopes = [...new Set(collectCssScopeIds(cssSource))]
        const missingScopes = jsScopes.filter(scope => !cssScopes.includes(scope))
        const extraScopes = cssScopes.filter(scope => !jsScopes.includes(scope))

        if (!missingScopes.length || missingScopes.length !== extraScopes.length) continue

        for (let index = 0; index < missingScopes.length; index += 1) {
          cssSource = cssSource.split(extraScopes[index]).join(missingScopes[index])
        }
        writeFileSync(cssPath, cssSource)
      }
    },
  }
}

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'AgentOpsAssistant',
      filename: 'remoteEntry.js',
      exposes: {
        './Config': './src/components/Config.vue',
        './Page': './src/components/Page.vue',
        './AppPage': './src/components/AppPage.vue',
        './Dashboard': './src/components/Dashboard.vue',
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
