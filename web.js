// Website adapter: Firebase sign-in (Google or email) + Firestore live sync for Luxe Café.
// Everyone in a "kitchen" (household) shares favorites, ratings, notes and the shopping list:
//   users/<uid>                     -> { householdId, name, color }
//   households/<hid>                -> { createdBy, createdAt, members: { <uid>: { name, color, joinedAt } } }
//   households/<hid>/marks/<recipe> -> { fav:{uid:ts}, rating:{uid:1-5}, note:{uid:{t,at}}, made:{uid:n} }
//   households/<hid>/shopping/<id>  -> { text, rid, done, by, at }
// The invite link is the site address + "#join-<hid>". No emails are stored in this public repo.
(function(){
  let resolveReady;
  window.LUXE_WEB={ready:new Promise(r=>resolveReady=r)};
  const COLORS=["#B8904A","#7E9A7A","#B96E52","#5E7790","#B77A8C","#7F6A9A"];

  // Get the newest version: iPhone home-screen apps hold on to old copies
  function checkVersion(){fetch("version.json?"+Date.now(),{cache:"no-store"}).then(r=>r.json()).then(j=>{
    if(j&&j.v&&window.APP_BUILD&&j.v!==window.APP_BUILD){let n=0;try{n=+sessionStorage.getItem("reloadFor"+j.v)||0;sessionStorage.setItem("reloadFor"+j.v,n+1);}catch(e){}
      if(n<3)location.replace(location.pathname+"?v="+encodeURIComponent(j.v)+location.hash);}}).catch(()=>{});}
  checkVersion();document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")checkVersion();});

  // Remember an invite link even if sign-in takes a few screens
  const m=location.hash.match(/^#join-([A-Za-z0-9]{12,40})$/);
  let JOIN=m?m[1]:null;
  try{if(JOIN)sessionStorage.setItem("lc-join",JOIN);else JOIN=sessionStorage.getItem("lc-join");}catch(e){}
  const clearJoin=()=>{JOIN=null;try{sessionStorage.removeItem("lc-join")}catch(e){} if(/^#join-/.test(location.hash))history.replaceState(null,"",location.pathname+location.search+"#recipes");};

  document.addEventListener("DOMContentLoaded",start);
  const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  function gate(html){let g=document.getElementById("gate");if(!g){g=document.createElement("div");g.id="gate";document.body.appendChild(g);}g.innerHTML=html;g.hidden=false;document.body.classList.add("lock");return g;}
  function hideGate(){const g=document.getElementById("gate");if(g)g.hidden=true;if(!document.querySelector(".page:not([hidden]),.brew:not([hidden])"))document.body.classList.remove("lock");}

  function start(){
    const cfg=window.FIREBASE_CONFIG;
    if(!cfg||!window.firebase){resolveReady(null);return;}
    firebase.initializeApp(cfg);
    const auth=firebase.auth(), fs=firebase.firestore(), FV=firebase.firestore.FieldValue;
    if(window.LUXE_EMULATOR){auth.useEmulator("http://127.0.0.1:9099");fs.useEmulator("127.0.0.1",8085);} // local testing only
    // Live sync: one open connection per device, long-polling where a network blocks streaming,
    // and a reconnect when the app comes back on screen.
    try{fs.settings({experimentalAutoDetectLongPolling:true,merge:true});}catch(e){}
    let lastKick=0;
    const kick=()=>{if(Date.now()-lastKick<3000)return;lastKick=Date.now();fs.disableNetwork().then(()=>fs.enableNetwork()).catch(()=>{});};
    document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")kick();});
    addEventListener("focus",kick);addEventListener("online",kick);addEventListener("pageshow",e=>{if(e.persisted)kick();});

    const HEAD=`<div class="gk" aria-hidden="true"></div>`;
    function showSignIn(err){
      gate(`<form class="gcard" id="gForm">${HEAD}<h2>Luxe Café</h2><p>${JOIN?"You've been invited to a shared coffee kitchen. Sign in to join.":"Recipes for our Ninja Luxe Café Pro. Sign in to sync favorites between phones."}</p>
        <button type="button" class="btn ggl" id="gGoogle"><svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.6 5.4 2.7 13.3l7.9 6.1C12.5 13.6 17.8 9.5 24 9.5z"/><path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.7c4.3-4 6.9-9.9 6.9-17.1z"/><path fill="#FBBC05" d="M10.6 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.8-4.6l-7.9-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.7 10.7l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.7c-2.1 1.4-4.8 2.3-8.5 2.3-6.2 0-11.5-4.1-13.4-9.8l-7.9 6.1C6.6 42.6 14.6 48 24 48z"/></svg>Continue with Google</button>
        <p class="gor">or use email</p>
        <label class="sr" for="gEmail">Email</label><input id="gEmail" type="email" autocomplete="username" placeholder="Email" required>
        <label class="sr" for="gPass">Password</label><input id="gPass" type="password" autocomplete="current-password" placeholder="Password (6+ characters)" required minlength="6">
        <p class="gerr" id="gErr" ${err?"":"hidden"}>${esc(err||"")}</p>
        <button type="submit" class="btn" id="gIn">Sign in</button>
        <button type="button" class="gsec" id="gNew">First time here? Create account</button>
        <button type="button" class="gsec" id="gReset">Forgot password</button></form>`);
      const E=()=>document.getElementById("gEmail").value.trim(),P=()=>document.getElementById("gPass").value;
      const fail=e=>{const msg={"auth/invalid-credential":"Wrong email or password.","auth/wrong-password":"Wrong email or password.","auth/user-not-found":"No account with that email. Tap Create account.","auth/email-already-in-use":"That email already has an account. Tap Sign in.","auth/weak-password":"Use at least 6 characters.","auth/invalid-email":"Check the email address.","auth/operation-not-allowed":"That sign-in method isn't turned on in Firebase yet.","auth/unauthorized-domain":"This website isn't on Firebase's authorized domains list yet.","auth/popup-blocked":"The Google window was blocked. Allow pop-ups and try again.","auth/account-exists-with-different-credential":"That email already signs in with a password. Use email below.","auth/network-request-failed":"No connection. Check your internet and try again."}[e.code]||e.message;
        const x=document.getElementById("gErr");x.textContent=msg;x.hidden=false;};
      document.getElementById("gGoogle").onclick=()=>{auth.signInWithPopup(new firebase.auth.GoogleAuthProvider()).catch(e=>{if(e.code==="auth/popup-closed-by-user"||e.code==="auth/cancelled-popup-request")return;fail(e);});};
      document.getElementById("gForm").onsubmit=ev=>{ev.preventDefault();auth.signInWithEmailAndPassword(E(),P()).catch(fail);};
      document.getElementById("gNew").onclick=()=>{if(!E()||P().length<6)return fail({message:"Type your email and a password (6+ characters) first."});auth.createUserWithEmailAndPassword(E(),P()).catch(fail);};
      document.getElementById("gReset").onclick=()=>{if(!E())return fail({message:"Type your email first."});auth.sendPasswordResetEmail(E()).then(()=>fail({message:"Check your email for a reset link."})).catch(fail);};
    }
    function showError(msg){gate(`<div class="gcard">${HEAD}<h2>Can't connect</h2><p>${esc(msg)}</p><button class="btn" id="gRetry">Try again</button><button class="gsec" id="gOut">Sign out</button></div>`);
      document.getElementById("gRetry").onclick=()=>location.reload();document.getElementById("gOut").onclick=()=>auth.signOut().then(()=>location.reload());}
    const friendly=e=>e&&e.code==="permission-denied"?"Firebase blocked the request. Paste the rules from firestore.rules into Firestore › Rules and publish them, then try again.":(e&&e.message)||"Something went wrong.";

    // First visit: name + color
    function askProfile(u,prev){return new Promise(res=>{
      const guess=prev.name||((u.displayName||"").split(" ")[0])||"";let color=prev.color||COLORS[0];
      gate(`<form class="gcard" id="pForm">${HEAD}<h2>Welcome</h2><p>What should we call you? Your name and color mark your favorites and notes.</p>
        <label class="sr" for="pIn">Your name</label><input id="pIn" type="text" maxlength="30" autocomplete="given-name" placeholder="Your first name" value="${esc(guess)}" required>
        <div class="swatches">${COLORS.map(c=>`<button type="button" class="sw" style="--c:${c}" data-c="${c}" aria-pressed="${c===color}" aria-label="Color ${c}"></button>`).join("")}</div>
        <button class="btn gold" type="submit">Continue</button></form>`);
      document.querySelectorAll("#pForm .sw").forEach(b=>b.onclick=()=>{color=b.dataset.c;document.querySelectorAll("#pForm .sw").forEach(x=>x.setAttribute("aria-pressed",x===b));});
      document.getElementById("pForm").onsubmit=ev=>{ev.preventDefault();const n=document.getElementById("pIn").value.trim().slice(0,30);if(n)res({name:n,color});};
    });}
    function askSwitch(){return new Promise(res=>{
      gate(`<div class="gcard">${HEAD}<h2>Join this kitchen?</h2><p>You're already in a kitchen. If you join this one, you'll share its favorites and shopping list instead. Your old favorites stay with your old kitchen.</p>
        <button class="btn gold" id="sJoin">Join the new kitchen</button><button class="gsec" id="sKeep">Keep my current kitchen</button></div>`);
      document.getElementById("sJoin").onclick=()=>res(true);document.getElementById("sKeep").onclick=()=>res(false);
    });}

    let unsubs=[], started=false;
    auth.onAuthStateChanged(async u=>{
      unsubs.forEach(f=>f());unsubs=[];
      if(!u){if(started){location.reload();return;}showSignIn();return;}
      started=true;
      gate(`<div class="gcard">${HEAD}<h2>Luxe Café</h2><p>Opening your kitchen…</p></div>`);
      try{
        const uref=fs.doc("users/"+u.uid);
        let prof=(await uref.get()).data()||{};
        if(!prof.name){const p=await askProfile(u,prof);prof=Object.assign(prof,p);await uref.set({name:prof.name,color:prof.color},{merge:true});}
        let hid=prof.householdId||null;
        const me={name:prof.name,color:prof.color||COLORS[0]};
        if(JOIN&&JOIN!==hid){
          if(!hid||await askSwitch()){
            try{await fs.doc("households/"+JOIN).set({members:{[u.uid]:Object.assign({joinedAt:Date.now()},me)}},{merge:true});hid=JOIN;await uref.set({householdId:hid},{merge:true});}
            catch(e){clearJoin();gate(`<div class="gcard">${HEAD}<h2>That invite didn't work</h2><p>The link may be incomplete. Ask for a fresh invite link, or continue with your own kitchen.</p><button class="btn" id="jOk">Continue</button></div>`);
              await new Promise(r=>document.getElementById("jOk").onclick=r);}
          }
        }
        clearJoin();
        if(!hid){const ref=fs.collection("households").doc();await ref.set({createdBy:u.uid,createdAt:Date.now(),members:{[u.uid]:Object.assign({joinedAt:Date.now()},me)}});hid=ref.id;await uref.set({householdId:hid},{merge:true});}
        hideGate();
        if(document.activeElement)document.activeElement.blur();
        resolveReady(liveBackend(u,hid,me));
      }catch(e){showError(friendly(e));}
    });

    function liveBackend(u,hid,me0){
      const H="households/"+hid,uid=u.uid,subs=[];
      let st={me:Object.assign({uid},me0),members:{[uid]:me0},marks:{},shopping:[],status:"connecting",error:""};
      const emit=()=>subs.forEach(f=>f(st));
      const err=e=>{st=Object.assign({},st,{status:"error",error:e&&e.code==="permission-denied"?"<b>Sync is blocked.</b> Paste the rules from firestore.rules into Firestore › Rules and tap Publish.":"<b>Sync stopped.</b> Check your connection; it reconnects by itself."});emit();};
      const ok=()=>{if(st.status!=="live"){st=Object.assign({},st,{status:"live",error:""});}};
      unsubs.push(fs.doc(H).onSnapshot(d=>{const m=(d.data()||{}).members||{};ok();st=Object.assign({},st,{members:m});const mine=m[uid];if(mine)st.me=Object.assign({uid},mine);emit();},err));
      unsubs.push(fs.collection(H+"/marks").onSnapshot(q=>{const mk={};q.forEach(d=>mk[d.id]=d.data());ok();st=Object.assign({},st,{marks:mk});emit();},err));
      unsubs.push(fs.collection(H+"/shopping").onSnapshot(q=>{const it=[];q.forEach(d=>it.push(Object.assign({id:d.id},d.data())));ok();st=Object.assign({},st,{shopping:it});emit();},err));
      const markRef=id=>fs.doc(H+"/marks/"+id);
      const setMap=(id,f,v)=>markRef(id).set({[f]:{[uid]:v==null?FV.delete():v}},{merge:true}).catch(err);
      return{mode:"live",email:u.email||"",
        subscribe(f){subs.push(f);f(st);},
        setFav:(id,on)=>setMap(id,"fav",on?Date.now():null),
        setRating:(id,n)=>setMap(id,"rating",n?n:null),
        setNote:(id,t)=>setMap(id,"note",t?{t:String(t).slice(0,2000),at:Date.now()}:null),
        addMade:id=>setMap(id,"made",FV.increment(1)),
        addItems(list){const b=fs.batch();list.forEach(x=>b.set(fs.collection(H+"/shopping").doc(),{text:String(x.text).slice(0,200),rid:x.rid||null,done:false,by:uid,at:Date.now()}));b.commit().catch(err);},
        toggleItem:(id,done)=>fs.doc(H+"/shopping/"+id).update({done:!!done}).catch(err),
        removeItem:id=>fs.doc(H+"/shopping/"+id).delete().catch(err),
        clearDone(){const b=fs.batch();st.shopping.filter(i=>i.done).forEach(i=>b.delete(fs.doc(H+"/shopping/"+i.id)));b.commit().catch(err);},
        updateProfile(p){const v={};if(p.name)v.name=String(p.name).slice(0,30);if(p.color)v.color=p.color;
          fs.doc("users/"+uid).set(v,{merge:true}).catch(err);fs.doc(H).set({members:{[uid]:v}},{merge:true}).catch(err);},
        inviteLink:()=>location.origin+location.pathname+"#join-"+hid,
        signOut:()=>auth.signOut().then(()=>location.replace(location.pathname))};
    }
  }
})();
