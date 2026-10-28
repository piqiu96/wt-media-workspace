import {createServer} from '/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/web/node_modules/vite/dist/node/index.js';
const root='/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/web';
const server=await createServer({root,configFile:root+'/vite.config.js',cacheDir:root+'/node_modules/.vite-modern-review',server:{host:'127.0.0.1',port:5190,strictPort:true}});await server.listen();console.log('UI review ready at 5190');
