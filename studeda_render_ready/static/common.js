
const $=(s,e=document)=>e.querySelector(s), $$=(s,e=document)=>[...e.querySelectorAll(s)];
const api=async(u,o={})=>{const r=await fetch(u,{headers:{"Content-Type":"application/json",...(o.headers||{})},...o});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||"Ошибка");return d};
function toast(m){const t=$("#toast");if(!t)return;t.textContent=m;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}
function fmt(n){return Math.round(Number(n)||0)}
function cid(){let id=localStorage.getItem("studedaClient");if(!id){id=(crypto.randomUUID?crypto.randomUUID():Date.now()+"-"+Math.random());localStorage.setItem("studedaClient",id)}return id}
const defaultGoals={calories:2200,protein:144,fat:63,carbs:259};
function getGoals(){try{return {...defaultGoals,...JSON.parse(localStorage.getItem("studedaGoals")||"{}")}}catch(e){return {...defaultGoals}}}
function saveGoals(g){localStorage.setItem("studedaGoals",JSON.stringify(g))}
function getPlan(){return localStorage.getItem("studedaPlan")==="premium"?"premium":"free"}
function applyPlan(){const p=getPlan();document.body.classList.toggle("premium-mode",p==="premium");$("#freeBtn")?.classList.toggle("active",p==="free");$("#premiumBtn")?.classList.toggle("active",p==="premium");window.dispatchEvent(new CustomEvent("planchange",{detail:{plan:p}}))}
function setPlan(p){localStorage.setItem("studedaPlan",p);applyPlan();toast(p==="premium"?"Premium включён ✦":"Обычный режим включён")}
function initDrawer(){
  $("#menuBtn")?.addEventListener("click",()=>{$("#drawer")?.classList.add("open");$("#drawerBack")?.classList.add("open")});
  $("#closeDrawer")?.addEventListener("click",closeDrawer);$("#drawerBack")?.addEventListener("click",closeDrawer);
  $("#freeBtn")?.addEventListener("click",()=>setPlan("free"));$("#premiumBtn")?.addEventListener("click",()=>setPlan("premium"));
}
function closeDrawer(){$("#drawer")?.classList.remove("open");$("#drawerBack")?.classList.remove("open")}
function nav(active){
  return `<nav class="bottom-nav">
  <a class="nav ${active==="today"?"active":""}" href="/today"><span class="nav-icon">⌂</span>Сегодня</a>
  <a class="nav ${active==="plan"?"active":""}" href="/plan"><span class="nav-icon">✦</span>План</a>
  <a class="nav ${active==="catalog"?"active":""}" href="/catalog"><span class="nav-icon">🛒</span>Корзина</a>
  <a class="nav" href="/today#addMeal"><span class="nav-icon">＋</span>Добавить</a>
  <a class="nav ${active==="reminders"?"active":""}" href="/reminders"><span class="nav-icon">◫</span>Напом.</a>
  </nav>`;
}
async function checkReminderNotifications(){
  if(!("Notification" in window))return;
  try{
    const rows=await api("/api/reminders?client_id="+encodeURIComponent(cid()));
    const now=new Date(),hm=now.toTimeString().slice(0,5),stamp=now.toISOString().slice(0,10)+hm;
    for(const r of rows){
      const key="studeda-notify-"+r.id+"-"+stamp;
      if(r.enabled&&r.reminder_time===hm&&!localStorage.getItem(key)){
        localStorage.setItem(key,"1");
        if(Notification.permission==="granted")new Notification("СтудЕда",{body:`${r.title} — пора поесть`})
      }
    }
  }catch(e){}
}
setInterval(checkReminderNotifications,30000);
document.addEventListener("DOMContentLoaded",()=>{initDrawer();applyPlan()});
