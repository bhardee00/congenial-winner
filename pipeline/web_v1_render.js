const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
const D=__dirname;const mode=process.argv[2]||'preview';
(async()=>{
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files']});
 const p=await b.newPage({viewport:{width:720,height:1280},deviceScaleFactor:1.5});
 p.on('console',m=>{if(m.type()==='error')console.log('PAGE',m.text())});p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+D+'/index.html');
 const tl=JSON.parse(fs.readFileSync(D+'/timeline.json'));await p.evaluate(t=>window.init(t),tl);
 if(mode==='preview'){
   const times=process.argv.slice(3).map(Number);
   for(const t of times){await p.evaluate(t=>window.renderAt(t),t);await p.screenshot({path:`${D}/prev_${t}.png`});}
 } else {
   const fps=30,N=Math.ceil(tl.total*fps);
   const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-i',D+'/voice.wav','-c:v','libx264','-pix_fmt','yuv420p','-preset','medium','-crf','20','-vf','scale=1080:1920:flags=lanczos','-c:a','aac','-b:a','160k','-shortest',process.argv[3]||D+'/out.mp4'],{stdio:['pipe','ignore','inherit']});
   const t0=Date.now();
   for(let f=0;f<N;f++){await p.evaluate(t=>window.renderAt(t),f/fps);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
     if(f%300===0)console.log('frame',f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');}
   ff.stdin.end();await new Promise(r=>ff.on('close',r));
 }
 await b.close();
})();
