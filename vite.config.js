import { defineConfig } from 'vite';
export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        background: 'src/background.js',
      },
      output: {
        entryFileNames: '[name].js', 
        dir: 'dist',                 
      },
    },
    emptyOutDir: true,
  }
});
