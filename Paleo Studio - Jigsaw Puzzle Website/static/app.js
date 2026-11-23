const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const cv=$('#cv'),ctx=cv.getContext('2d',{willReadFrequently:true});
const mk=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c};
const PAL=['#C8553D','#E9A23B','#2F7F6F','#3D5A80','#7B2D26','#6B4E71','#93B7BE','#12302A'];
const STK=[['Rexie','#2F7F6F','🔥'],['Trike','#C8553D','🌿'],['Steggy','#3D5A80','⭐'],['Bronto','#6B4E71','🌴'],['Raptor','#E9A23B','⚡'],['Ptera','#5F8FA0','☁️'],['Anky','#7B2D26','🦴'],['Spino','#12302A','🌋']];
let sid,W,H,img,stamps=[],mode='paint',col=PAL[0],stamp='rex',ssize=48,muted=false,seed=0;
let grid=4,pcs=[],drag=null,bx=0,by=0,cw=0,ch=0,t0=0,won=false,tm=0,sc;

/* ---- sound (WebAudio synth, no files) ---- */
const AC=window.AudioContext||window.webkitAudioContext;let ac;
function tone(f,d=.12,type='sine',v=.12,at=0){if(muted||!AC)return;ac=ac||new AC();const o=ac.createOscillator(),g=ac.createGain(),t=ac.currentTime+at;o.type=type;o.frequency.value=f;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(ac.destination);o.start(t);o.stop(t+d)}
const sfx={pop:()=>tone(540,.09,'triangle'),stamp:()=>{tone(120,.16,'square',.07);tone(80,.22,'sine',.14)},snap:()=>{tone(660,.08,'triangle');tone(990,.14,'sine',.1,.07)},win:()=>[523,659,784,1047,1319].forEach((f,i)=>tone(f,.3,'triangle',.13,i*.11)),award:()=>[784,988,1175].forEach((f,i)=>tone(f,.25,'sine',.12,i*.09))};
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('on'),3000)}
const api=(u,b)=>fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b||{})});

/* ---- canvas ---- */
async function refresh(){const b=await (await fetch(`/api/image/${sid}?t=${Date.now()}`)).blob(),i=new Image();i.src=URL.createObjectURL(b);await i.decode();img=i;redraw()}
function redraw(){ctx.drawImage(img,0,0);stamps.forEach(drawStamp)}
const poly=(g,p)=>{p.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath()};
const dot=(g,x,y,r)=>{g.moveTo(x+r,y);g.arc(x,y,r,0,7)};
const ST={
 rex:g=>poly(g,[[-.62,.1],[-.3,-.05],[0,-.22],[.15,-.4],[.3,-.52],[.58,-.46],[.58,-.28],[.32,-.24],[.24,-.04],[.4,.02],[.2,.2],[.22,.58],[.34,.62],[-.02,.62],[-.04,.3],[-.2,.58],[-.12,.62],[-.4,.62],[-.34,.3]]),
 foot:g=>{g.ellipse(0,.3,.34,.3,0,0,7);poly(g,[[-.5,-.05],[-.38,-.6],[-.2,-.1]]);poly(g,[[-.12,-.15],[0,-.8],[.12,-.15]]);poly(g,[[.2,-.1],[.38,-.6],[.5,-.05]])},
 egg:g=>g.ellipse(0,.08,.46,.6,0,0,7),
 bone:g=>{g.rect(-.4,-.1,.8,.2);[[-.45,-.14],[-.45,.14],[.45,-.14],[.45,.14]].forEach(([x,y])=>dot(g,x,y,.14))},
 frond:g=>{g.ellipse(-.2,0,.17,.6,.5,0,7);g.closePath();g.ellipse(.2,0,.17,.6,-.5,0,7)}
};
function drawStamp(s){ctx.save();ctx.translate(s.x,s.y);ctx.rotate(s.r);ctx.scale(s.s,s.s);ctx.beginPath();ST[s.k](ctx);ctx.fillStyle=s.c;ctx.fill();ctx.restore()}
const pt=e=>{const r=cv.getBoundingClientRect();return[(e.clientX-r.left)*cv.width/r.width,(e.clientY-r.top)*cv.height/r.height]};

/* ---- jigsaw ---- */
function edge(g,x0,y0,x1,y1,s){
  if(!s){g.lineTo(x1,y1);return}
  const ex=x1-x0,ey=y1-y0,p=(u,v)=>[x0+ex*u+ey*v*s,y0+ey*u-ex*v*s],B=(a,b,c)=>g.bezierCurveTo(...p(...a),...p(...b),...p(...c));
  g.lineTo(...p(.34,0));B([.4,0],[.36,.1],[.4,.14]);B([.3,.22],[.42,.3],[.5,.3]);B([.58,.3],[.7,.22],[.6,.14]);B([.64,.1],[.6,0],[.66,0]);g.lineTo(x1,y1)
}
function mkPuzzle(){
  clearInterval(tm);won=false;drag=null;cv.width=W;cv.height=H;redraw();
  sc=mk(W,H);sc.getContext('2d').drawImage(cv,0,0);
  const n=grid;cw=W/n;ch=H/n;const pad=Math.ceil(Math.max(cw,ch)*.32)+2,SW=Math.round(W*1.5),SH=Math.round(H*1.4);
  cv.width=SW;cv.height=SH;bx=(SW-W)/2;by=(SH-H)/2;
  const rs=()=>Math.random()<.5?1:-1,T=[],L=[];
  for(let r=0;r<=n;r++){T[r]=[];L[r]=[];for(let c=0;c<=n;c++){T[r][c]=r&&r<n?rs():0;L[r][c]=c&&c<n?rs():0}}
  pcs=[];
  for(let r=0;r<n;r++)for(let c=0;c<n;c++){
    const x=c*cw,y=r*ch,pc=mk(Math.ceil(cw+2*pad),Math.ceil(ch+2*pad)),g=pc.getContext('2d',{willReadFrequently:true});
    g.translate(pad-x,pad-y);g.beginPath();g.moveTo(x,y);
    edge(g,x,y,x+cw,y,T[r][c]);edge(g,x+cw,y,x+cw,y+ch,-L[r][c+1]);edge(g,x+cw,y+ch,x,y+ch,-T[r+1][c]);edge(g,x,y+ch,x,y,L[r][c]);g.closePath();
    g.save();g.clip();g.drawImage(sc,0,0);g.restore();
    g.lineWidth=2;g.strokeStyle='rgba(255,255,255,.7)';g.stroke();g.lineWidth=1;g.strokeStyle='rgba(0,0,0,.35)';g.stroke();
    let px,py,k=0;do{px=Math.random()*(SW-pc.width);py=Math.random()*(SH-pc.height);k++}while(k<30&&px+pc.width/2>bx&&px+pc.width/2<bx+W&&py+pc.height/2>by&&py+pc.height/2<by+H);
    pcs.push({c:pc,x:px,y:py,hx:bx+x-pad,hy:by+y-pad,l:false});
  }
  t0=Date.now();drawP();status();tm=setInterval(status,500);
}
function drawP(){
  ctx.fillStyle='#F4F6F2';ctx.fillRect(0,0,cv.width,cv.height);
  if($('#guide').checked){ctx.save();ctx.globalAlpha=.14;ctx.drawImage(sc,bx,by);ctx.restore()}
  ctx.setLineDash([8,6]);ctx.strokeStyle='#8a9a92';ctx.lineWidth=2;ctx.strokeRect(bx,by,W,H);ctx.setLineDash([]);
  for(const p of pcs){if(!p.l){ctx.shadowColor='rgba(18,48,42,.35)';ctx.shadowBlur=10;ctx.shadowOffsetY=4}ctx.drawImage(p.c,p.x,p.y);ctx.shadowColor='transparent';ctx.shadowBlur=0;ctx.shadowOffsetY=0}
}
function status(){if(won)return;const d=pcs.filter(p=>p.l).length,s=Math.floor((Date.now()-t0)/1000);$('#pst').textContent=`${d} of ${pcs.length} placed, ${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`}
function hit(x,y){for(let i=pcs.length-1;i>=0;i--){const p=pcs[i];if(p.l)continue;const a=Math.floor(x-p.x),b=Math.floor(y-p.y);if(a<0||b<0||a>=p.c.width||b>=p.c.height)continue;if(p.c.getContext('2d').getImageData(a,b,1,1).data[3]>40)return i}return -1}
async function win(){
  won=true;clearInterval(tm);drawP();ctx.drawImage(sc,bx,by);sfx.win();
  const d=await (await api('/api/stickers/award')).json();
  $('#pst').textContent='Specimen assembled';
  if(d.new!=null){setTimeout(sfx.award,700);toast('New sticker unlocked: '+STK[d.new][0])}else toast('Puzzle solved. Your collection is complete!');
}

/* ---- pointer ---- */
cv.addEventListener('pointerdown',async e=>{
  if(!sid)return;const[x,y]=pt(e);
  if(mode==='paint'){await api(`/api/fill/${sid}`,{x:Math.round(x),y:Math.round(y),color:col});sfx.pop();refresh()}
  else if(mode==='stamp'){const s={k:stamp,x,y,s:ssize,c:col,r:(Math.random()-.5)*.7};stamps.push(s);drawStamp(s);sfx.stamp()}
  else if(mode==='puzzle'&&!won){const i=hit(x,y);if(i<0)return;const p=pcs.splice(i,1)[0];pcs.push(p);drag={p,dx:x-p.x,dy:y-p.y};cv.setPointerCapture(e.pointerId);drawP()}
});
cv.addEventListener('pointermove',e=>{if(!drag)return;const[x,y]=pt(e);drag.p.x=x-drag.dx;drag.p.y=y-drag.dy;drawP()});
function release(){
  if(!drag)return;const p=drag.p;drag=null;
  if(Math.hypot(p.x-p.hx,p.y-p.hy)<Math.max(cw,ch)*.22){p.x=p.hx;p.y=p.hy;p.l=true;pcs.splice(pcs.indexOf(p),1);pcs.unshift(p);sfx.snap()}
  drawP();status();if(pcs.every(q=>q.l))win();
}
cv.addEventListener('pointerup',release);cv.addEventListener('pointercancel',release);

/* ---- modes, notes, collection ---- */
function setMode(m){
  clearInterval(tm);mode=m;
  $$('#rail [data-m]').forEach(b=>b.classList.toggle('on',b.dataset.m===m));
  ['paint','stamp','puzzle','book'].forEach(k=>$('#t-'+k).hidden=k!==m);
  $('#t-sw').hidden=!(m==='paint'||m==='stamp'||!sid&&m==='paint');
  $('#drop').hidden=!!sid||m==='book';$('#plate').hidden=m==='book'||!sid;$('#book').hidden=m!=='book';
  if(m==='book')return shelf();
  if(!sid)return;
  cv.style.touchAction=m==='puzzle'?'none':'auto';
  if(m==='puzzle')mkPuzzle();else{cv.width=W;cv.height=H;redraw()}
}
function notes(i){
  $('#cap').innerHTML=`<em>Fig. 1.</em> ${i.name}`;
  $('#notes').innerHTML=`<dt>Shapes found</dt><dd>${i.shapes}</dd><dt>Ink coverage</dt><dd>${i.ink}%</dd><dt>Symmetry</dt><dd>${i.symmetry}%</dd><dt>Suggested jigsaw</dt><dd>${i.grid}×${i.grid}</dd>`;
  grid=i.grid;$$('#grids .chip').forEach(c=>c.classList.toggle('on',+c.dataset.g===grid));
}
const sticker=([n,c,e],on)=>`<div class="stk ${on?'':'lock'}"><svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="37" fill="${on?c:'#9aa7a1'}" fill-opacity=".14" stroke="${on?c:'#9aa7a1'}" stroke-width="2"/>${on?`<g fill="${c}"><ellipse cx="38" cy="47" rx="20" ry="13"/><circle cx="55" cy="34" r="10"/><path d="M20 47L6 54l16-3zM30 35l4-9 4 9zM40 34l4-10 4 10z"/></g><circle cx="58" cy="32" r="2.2" fill="#fff"/><text x="60" y="68" font-size="15">${e}</text>`:'<text x="40" y="52" text-anchor="middle" font-size="30" fill="#9aa7a1">?</text>'}</svg><b>${on?n:'Locked'}</b></div>`;
async function shelf(){const d=await (await fetch('/api/stickers')).json();$('#grid').innerHTML=STK.map((s,i)=>sticker(s,d.owned.includes(i))).join('');$('#cnt').textContent=`${d.owned.length} of ${STK.length} collected`}

/* ---- upload ---- */
async function upload(f){
  const fd=new FormData();fd.append('file',f,f.name||'doodle.png');
  const r=await fetch('/api/analyze',{method:'POST',body:fd});if(!r.ok)return toast('That file could not be read as an image');
  const d=await r.json();sid=d.id;W=d.w;H=d.h;stamps=[];seed=d.info.seed;notes(d.info);
  const t=await (await api(`/api/auto/${sid}`,{seed})).json();await refresh();setMode('paint');toast('Smart colorist palette: '+t.theme);
}
$('#pick').onclick=()=>$('#file').click();
$('#file').onchange=e=>e.target.files[0]&&upload(e.target.files[0]);
const dz=$('#drop');
['dragenter','dragover'].forEach(v=>dz.addEventListener(v,e=>{e.preventDefault();dz.classList.add('over')}));
['dragleave','drop'].forEach(v=>dz.addEventListener(v,e=>{e.preventDefault();dz.classList.remove('over')}));
dz.addEventListener('drop',e=>{const f=e.dataTransfer.files[0];f&&upload(f)});
addEventListener('paste',e=>{const it=[...(e.clipboardData?.items||[])].find(i=>i.type.startsWith('image/'));it&&upload(it.getAsFile())});
$('#sample').onclick=()=>{
  const c=mk(560,420),x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,560,420);x.strokeStyle=x.fillStyle='#222';x.lineWidth=5;x.lineCap=x.lineJoin='round';
  const P=(...a)=>{x.beginPath();x.moveTo(a[0],a[1]);for(let i=2;i<a.length;i+=2)x.lineTo(a[i],a[i+1]);x.stroke()};
  x.beginPath();x.ellipse(260,260,120,85,0,0,7);x.stroke();x.beginPath();x.ellipse(395,165,58,46,-.2,0,7);x.stroke();
  P(150,235,40,300,156,292);P(215,335,210,388,262,388,258,342);P(300,336,296,388,348,388,340,320);
  [200,255,310].forEach(X=>{const yb=260-85*Math.sqrt(1-((X-260)/120)**2);P(X-20,yb+5,X,yb-42,X+20,yb+5)});
  x.beginPath();x.arc(412,152,4,0,7);x.fill();x.beginPath();x.arc(414,172,16,.2,2.5);x.stroke();
  x.beginPath();x.arc(90,80,34,0,7);x.stroke();for(let i=0;i<10;i++){const a=i*.628;P(90+Math.cos(a)*46,80+Math.sin(a)*46,90+Math.cos(a)*64,80+Math.sin(a)*64)}
  x.beginPath();x.moveTo(15,402);for(let i=0;i<=27;i++)x.lineTo(15+i*20,402+Math.sin(i*.9)*5);x.stroke();
  c.toBlob(b=>upload(b));
};

/* ---- wiring ---- */
$$('#rail [data-m]').forEach(b=>b.onclick=()=>setMode(b.dataset.m));
$('#new').onclick=()=>{sid=null;setMode('paint')};
$('#mute').onclick=e=>{muted=!muted;e.target.textContent=muted?'Sound off':'Sound on'};
PAL.forEach((c,i)=>{const b=document.createElement('button');b.className='sw'+(i?'':' on');b.style.background=c;b.setAttribute('aria-label','Ink '+(i+1));b.onclick=()=>{col=c;$$('.sw').forEach(s=>s.classList.toggle('on',s===b))};$('#sws').appendChild(b)});
$('#auto').onclick=async()=>{if(!sid)return;seed++;const t=await (await api(`/api/auto/${sid}`,{seed})).json();await refresh();sfx.pop();toast('Palette: '+t.theme)};
$('#clear').onclick=async()=>{if(!sid)return;await api(`/api/clear/${sid}`);refresh()};
$('#stamps').onclick=e=>{const b=e.target.closest('[data-k]');if(!b)return;stamp=b.dataset.k;$$('#stamps button').forEach(x=>x.classList.toggle('on',x===b))};
$('#ss').oninput=e=>ssize=+e.target.value;
$('#grids').onclick=e=>{const b=e.target.closest('[data-g]');if(!b)return;grid=+b.dataset.g;$$('#grids .chip').forEach(c=>c.classList.toggle('on',c===b));mkPuzzle()};
$('#shuf').onclick=mkPuzzle;
$('#guide').onchange=()=>{if(!won&&mode==='puzzle')drawP()};
setMode('paint');
