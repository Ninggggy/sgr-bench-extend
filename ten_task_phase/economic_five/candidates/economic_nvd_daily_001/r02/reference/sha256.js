function sha256(text) {
 const bytes=unescape(encodeURIComponent(text)), words=[], H=[], K=[];
 function prime(n){for(let j=2;j*j<=n;j++)if(n%j===0)return false;return true;}
 for(let n=2;K.length<64;n++)if(prime(n)){if(H.length<8)H.push((Math.sqrt(n)%1*4294967296)|0);K.push((Math.cbrt(n)%1*4294967296)|0);}
 for(let i=0;i<bytes.length;i++)words[i>>2]=(words[i>>2]||0)|(bytes.charCodeAt(i)<<(24-8*(i%4)));
 words[bytes.length>>2]=(words[bytes.length>>2]||0)|(0x80<<(24-8*(bytes.length%4)));
 const end=(((bytes.length+8)>>6)+1)*16;words[end-1]=bytes.length*8;words[end-2]=Math.floor(bytes.length/536870912);
 const rot=(x,n)=>(x>>>n)|(x<<(32-n));
 for(let off=0;off<end;off+=16){const w=[];for(let i=0;i<64;i++){if(i<16)w[i]=words[off+i]|0;else{const x=w[i-15],y=w[i-2],s0=rot(x,7)^rot(x,18)^(x>>>3),s1=rot(y,17)^rot(y,19)^(y>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)|0;}}
 let [a,b,c,d,e,f,g,h]=H;
 for(let i=0;i<64;i++){const s1=rot(e,6)^rot(e,11)^rot(e,25),ch=(e&f)^(~e&g),t1=(h+s1+ch+K[i]+w[i])|0,s0=rot(a,2)^rot(a,13)^rot(a,22),maj=(a&b)^(a&c)^(b&c),t2=(s0+maj)|0;h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0;}
 const next=[a,b,c,d,e,f,g,h];for(let i=0;i<8;i++)H[i]=(H[i]+next[i])|0;
 }
 return H.map(x=>(x>>>0).toString(16).padStart(8,"0")).join("");
}
