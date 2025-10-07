/// <reference types="vite/client" />

// (опционально, чтобы TS знал про твою переменную)
interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
