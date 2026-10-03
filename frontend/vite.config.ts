import {defineConfig} from "vite";
import react from "@vitejs/plugin-react";
import {fileURLToPath,URL} from "node:url";
export default defineConfig({base:process.env.BASE_PATH||"/",plugins:[react()],resolve:{alias:{"@":fileURLToPath(new URL(".",import.meta.url))}},build:{target:"es2022"}});
