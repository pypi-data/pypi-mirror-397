import * as esbuild from 'esbuild';
import { existsSync, mkdirSync } from 'fs';

const isWatch = process.argv.includes('--watch');
const outdir = '../out/webview-ui';

// Ensure output directory exists
if (!existsSync(outdir)) {
    mkdirSync(outdir, { recursive: true });
}

const buildOptions = {
    entryPoints: ['./src/stageEditor/index.tsx'],
    bundle: true,
    outfile: `${outdir}/stageEditor.js`,
    minify: !isWatch,
    sourcemap: isWatch,
    target: 'es2020',
    format: 'iife',
    define: {
        'process.env.NODE_ENV': isWatch ? '"development"' : '"production"',
    },
    loader: {
        '.tsx': 'tsx',
        '.ts': 'ts',
        '.css': 'css',
    },
    jsx: 'automatic',
    jsxImportSource: 'react',
};

if (isWatch) {
    const ctx = await esbuild.context(buildOptions);
    await ctx.watch();
    console.log('Watching for changes...');
} else {
    await esbuild.build(buildOptions);
    console.log('Build complete!');
}
