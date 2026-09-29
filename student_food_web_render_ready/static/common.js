
const $=(s,e=document)=>e.querySelector(s), $$=(s,e=document)=>[...e.querySelectorAll(s)];

const api=async(u,o={})=>{
  const r=await fetch(u,{headers:{"Content-Type":"application/json",...(o.headers||{})},...o});
  const d=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(d.error||"Ошибка");
  return d;
};

function toast(m){
  const t=$("#toast");
  if(!t)return;
  t.textContent=m;
  t.classList.add("show");
  clearTimeout(window.__tt);
  window.__tt=setTimeout(()=>t.classList.remove("show"),2200);
}
function fmt(n){return Math.round(Number(n)||0)}

const DEFAULT_GOALS={calories:2400,protein:150,fat:80,carbs:300};

function getPlan(){
  return localStorage.getItem("studentFuelPlan")==="premium" ? "premium" : "free";
}
function getGoals(){
  try{
    return {...DEFAULT_GOALS,...JSON.parse(localStorage.getItem("studentFuelGoals")||"{}")};
  }catch(e){
    return {...DEFAULT_GOALS};
  }
}
function saveGoals(goals){
  localStorage.setItem("studentFuelGoals",JSON.stringify(goals));
}
function applyPlan(){
  const plan=getPlan();
  document.body.classList.toggle("premium-mode",plan==="premium");
  $$(".plan-toggle").forEach(btn=>{
    btn.innerHTML=plan==="premium" ? "👑 PREMIUM" : "FREE";
    btn.title=plan==="premium" ? "Переключиться на обычную версию" : "Переключиться на Premium";
    btn.classList.toggle("is-premium",plan==="premium");
  });
  window.dispatchEvent(new CustomEvent("planchange",{detail:{plan}}));
}
function togglePlan(){
  const next=getPlan()==="premium" ? "free" : "premium";
  localStorage.setItem("studentFuelPlan",next);
  applyPlan();
  toast(next==="premium" ? "Premium включён 👑" : "Обычная версия включена");
}
function initPlanSwitch(){
  $$(".plan-toggle").forEach(btn=>btn.addEventListener("click",togglePlan));
  applyPlan();
}

async function checkReminderNotifications(){
  if(!("Notification" in window))return;
  try{
    const rows=await api("/api/reminders"),now=new Date(),hm=now.toTimeString().slice(0,5),
      stamp=now.toISOString().slice(0,10)+hm;
    for(const r of rows){
      const key="studentFuel:"+r.id+":"+stamp;
      if(r.enabled&&r.reminder_time===hm&&!localStorage.getItem(key)){
        localStorage.setItem(key,"1");
        if(Notification.permission==="granted"){
          new Notification("Student Fuel",{body:`${r.title} — пора поесть 🍽️`});
        }
      }
    }
  }catch(e){}
}
setInterval(checkReminderNotifications,30000);

document.addEventListener("DOMContentLoaded",initPlanSwitch);
