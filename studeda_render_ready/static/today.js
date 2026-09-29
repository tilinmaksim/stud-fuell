
$("#nav").innerHTML=nav("today");
const now=new Date();const date=now.toISOString().slice(0,10);
$("#todayTitle").textContent="Сегодня, "+now.toLocaleDateString("ru-RU",{day:"2-digit",month:"2-digit"});
$("#mealTime").value=now.toTimeString().slice(0,5);

let lastSums={calories:0,protein:0,fat:0,carbs:0};

function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function updateHero(){
  const g=getGoals();
  $("#goalKcal").textContent=fmt(g.calories);
  $("#totalKcal").textContent=fmt(lastSums.calories);
  $("#carbChip").textContent=fmt(lastSums.carbs)+" г";
  $("#proteinChip").textContent=fmt(lastSums.protein)+" г";
  $("#fatChip").textContent=fmt(lastSums.fat)+" г";
  const c=lastSums.carbs*4,p=lastSums.protein*4,f=lastSums.fat*9,total=Math.max(c+p+f,1);
  const cPct=(c/total)*100,pPct=(p/total)*100;
  $("#macroRing").style.background=`conic-gradient(var(--purple) 0 ${cPct}%, var(--pink) ${cPct}% ${cPct+pPct}%, var(--peach) ${cPct+pPct}% 100%)`;
}
async function load(){
  const rows=await api(`/api/meals?client_id=${encodeURIComponent(cid())}&date=${date}`);
  lastSums=rows.reduce((a,r)=>({calories:a.calories+Number(r.calories||0),protein:a.protein+Number(r.protein||0),fat:a.fat+Number(r.fat||0),carbs:a.carbs+Number(r.carbs||0)}),{calories:0,protein:0,fat:0,carbs:0});
  updateHero();
  $("#mealCount").textContent=`${rows.length} записей`;
  const l=$("#mealList");
  if(!rows.length){l.innerHTML='<div class="empty">Сегодня пока ничего не записано.<br>Добавь первый приём пищи.</div>';return}
  l.innerHTML=rows.map(r=>`<div class="item"><div class="item-icon">🍽️</div><div class="item-main"><b>${esc(r.product_name)}</b><div class="meta">${r.meal_time} · ${fmt(r.calories)} ккал<br>Б ${fmt(r.protein)} · Ж ${fmt(r.fat)} · У ${fmt(r.carbs)}</div></div><button class="del" data-del="${r.id}">✕</button></div>`).join("");
  $$("[data-del]").forEach(b=>b.onclick=async()=>{await api(`/api/meals/${b.dataset.del}?client_id=${encodeURIComponent(cid())}`,{method:"DELETE"});toast("Запись удалена");load()})
}
$("#saveMeal").onclick=async()=>{
  try{
    await api("/api/meals",{method:"POST",body:JSON.stringify({client_id:cid(),meal_date:date,meal_time:$("#mealTime").value,product_name:$("#product").value,calories:$("#kcal").value||0,protein:$("#protein").value||0,fat:$("#fat").value||0,carbs:$("#carbs").value||0})});
    ["product","kcal","protein","fat","carbs"].forEach(x=>$("#"+x).value="");
    toast("Добавлено в рацион");load()
  }catch(e){toast(e.message)}
};
$("#startBtn").onclick=()=>document.querySelector("#addMeal").scrollIntoView({behavior:"smooth"});
$("#logBtn").onclick=()=>document.querySelector("#addMeal").scrollIntoView({behavior:"smooth"});
window.addEventListener("planchange",updateHero);
const q=new URLSearchParams(location.search);
if(q.get("name")){$("#product").value=q.get("name")||"";$("#kcal").value=q.get("kcal")||"";$("#protein").value=q.get("p")||"";$("#fat").value=q.get("f")||"";$("#carbs").value=q.get("c")||"";setTimeout(()=>document.querySelector("#addMeal").scrollIntoView({behavior:"smooth"}),150)}
load();
