// Builds index.html (the website) from app-src.html, the recipe data and the photos in images/.
// Run: node build.js
const fs=require("fs");
const src=fs.readFileSync("app-src.html","utf8");
const data=JSON.parse(fs.readFileSync("recipes/recipes.json","utf8"));
const photos=fs.existsSync("images")?fs.readdirSync("images").filter(f=>f.endsWith(".webp")).map(f=>f.slice(0,-5)).sort():[];
const ids=new Set(data.recipes.map(r=>r.id));
const stray=photos.filter(p=>!ids.has(p));
if(stray.length)console.warn("Photos with no matching recipe id:",stray.join(", "));
// Photographer credits (Unsplash License: free to use, credit appreciated): images/credits.json
const cred=fs.existsSync("images/credits.json")?JSON.parse(fs.readFileSync("images/credits.json","utf8")):{};
const credits={};for(const p of photos)if(cred[p])credits[p]=[cred[p].by,cred[p].page];
// Firebase sign-in loads a helper frame from the project's auth domain.
const cfg=fs.existsSync("firebase-config.js")?fs.readFileSync("firebase-config.js","utf8"):"";
const authDomain=(cfg.match(/authDomain:\s*"([^"]+)"/)||[])[1];
const FB="https://www.gstatic.com/firebasejs/10.14.1/";
const csp=["default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://www.gstatic.com https://apis.google.com https://www.google.com",
  "connect-src 'self' https://*.googleapis.com https://*.firebaseio.com https://www.gstatic.com wss://*.firebaseio.com",
  "frame-src "+(authDomain?"https://"+authDomain+" ":"")+"https://accounts.google.com https://apis.google.com https://www.google.com",
  "img-src 'self' data: blob: https://*.googleusercontent.com https://www.gstatic.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com","font-src https://fonts.gstatic.com",
  "object-src 'none'","base-uri 'self'","form-action 'self'"].join("; ");
const V=(src.match(/const APP_V="([^"]+)"/)||[])[1]||"0";
const json=s=>JSON.stringify(s).replace(/</g,"\\u003c");
const head=`<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Luxe Café</title>
<meta name="description" content="Our recipes for the Ninja Luxe Café Pro.">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Luxe Café">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#E7E3DC">
<meta http-equiv="Content-Security-Policy" content="${csp}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="apple-touch-icon" href="icon-180.png"><link rel="icon" href="icon-180.png"><link rel="manifest" href="manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Marcellus&display=swap">
<script>window.APP_BUILD=${json(V)};try{var t=JSON.parse(localStorage.getItem("lc-theme"));if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>
<script>window.RECIPES=${json(data)};window.PHOTOS=${json(photos)};window.CREDITS=${json(credits)};</script>
<script src="firebase-config.js"></script>
<script src="${FB}firebase-app-compat.js"></script>
<script src="${FB}firebase-auth-compat.js"></script>
<script src="${FB}firebase-firestore-compat.js"></script>
<script src="web.js"></script>
</head><body>
`;
fs.writeFileSync("version.json",JSON.stringify({v:V})+"\n");
fs.writeFileSync("index.html",head+src+"\n</body></html>\n");
console.log(`index.html built: version ${V}, ${data.recipes.length} recipes, ${photos.length} photos`);
