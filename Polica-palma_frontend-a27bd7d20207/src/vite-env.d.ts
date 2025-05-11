interface ImportMetaEnv {
  VITE_API_URL: string
  VITE_DEV_API_URL: string
}

declare module 'vite' {
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}