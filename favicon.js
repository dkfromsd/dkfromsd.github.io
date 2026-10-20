/* 탭 아이콘 애니메이션: 코파카바나의 해와 물결. Chrome·Edge는 SVG 파비콘 애니메이션을 재생하지 않으므로 canvas로 프레임을 그려 바꿔 끼운다. */
(function(){
  var link=document.querySelector('link[rel="icon"]');
  if(!link||!document.createElement('canvas').getContext)return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var S=64,c=document.createElement('canvas');c.width=c.height=S;
  var g=c.getContext('2d'),t0=performance.now(),timer=null;
  function rr(x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();}
  function frame(){
    var t=(performance.now()-t0)/1000;
    g.clearRect(0,0,S,S);g.save();rr(0,0,S,S,14);g.clip();
    g.fillStyle='#1d6766';g.fillRect(0,0,S,S);
    g.fillStyle='#f0a463';g.beginPath();g.arc(40,20-1.25*(1-Math.cos(t/3.6*2*Math.PI)),11,0,7);g.fill();
    g.strokeStyle='#f6efe3';g.lineWidth=5;g.lineCap='round';
    [[43,0],[56,.9]].forEach(function(w){
      var ph=((t+w[1])/2.4)*2*Math.PI;g.beginPath();
      for(var x=-4;x<=S+4;x+=2){var y=w[0]+4*Math.sin(x/32*2*Math.PI+ph);x<=-4?g.moveTo(x,y):g.lineTo(x,y);}
      g.stroke();
    });
    g.restore();link.href=c.toDataURL('image/png');
  }
  function start(){if(!timer){frame();timer=setInterval(frame,125);}}
  function stop(){clearInterval(timer);timer=null;}
  document.addEventListener('visibilitychange',function(){document.hidden?stop():start();});
  start();
})();
