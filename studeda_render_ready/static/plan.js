
$("#nav").innerHTML=nav("plan");
function fillGoals(){const g=getGoals();$("#goalCalories")&&($("#goalCalories").value=g.calories);$("#goalProtein")&&($("#goalProtein").value=g.protein);$("#goalFat")&&($("#goalFat").value=g.fat);$("#goalCarbs")&&($("#goalCarbs").value=g.carbs)}
$("#enablePremium").onclick=()=>setPlan("premium");
$("#saveGoals")?.addEventListener("click",()=>{saveGoals({calories:Number($("#goalCalories").value)||2200,protein:Number($("#goalProtein").value)||144,fat:Number($("#goalFat").value)||63,carbs:Number($("#goalCarbs").value)||259});toast("Цели сохранены");loadWeek()});
async function loadWeek(){
  if(getPlan()!=="premium")return;
  const end=new Date(),days=[];
  for(let i=6;i>=0;i--){
    const d=new Date(end);d.setDate(end.getDate()-i);const iso=d.toISOString().slice(0,10);
    const rows=await api(`/api/meals?client_id=${encodeURIComponent(cid())}&date=${iso}`);
    const s=rows.reduce((a,r)=>({k:a.k+Number(r.calories||0),p:a.p+Number(r.protein||0)}),{k:0,p:0});
    days.push({d,k:s.k,p:s.p,t:rows.length>0});
  }
  const tracked=days.filter(x=>x.t);const ak=tracked.length?tracked.reduce((s,x)=>s+x.k,0)/tracked.length:0;const ap=tracked.length?tracked.reduce((s,x)=>s+x.p,0)/tracked.length:0;
  $("#avgKcal").textContent=fmt(ak);$("#avgProtein").textContent=fmt(ap)+" г";$("#tracked").textContent=`${tracked.length}/7`;
  const g=getGoals(),labels=["Вс","Пн","Вт","Ср","Чт","Пт","Сб"];
  $("#weekChart").innerHTML=days.map(x=>`<div class="day"><div class="bar-wrap"><div class="bar" style="height:${Math.max(3,Math.min(100,(x.k/Math.max(g.calories,1))*100))}%"></div></div><small>${labels[x.d.getDay()]}</small></div>`).join("");
}
async function smartPick(){
  const g=getGoals(),date=new Date().toISOString().slice(0,10);
  const meals=await api(`/api/meals?client_id=${encodeURIComponent(cid())}&date=${date}`);
  const used=meals.reduce((a,r)=>({k:a.k+Number(r.calories||0),p:a.p+Number(r.protein||0)}),{k:0,p:0});
  const leftK=Math.max(0,g.calories-used.k),leftP=Math.max(0,g.protein-used.p);
  const recipes=await api("/api/catalog?kind="+encodeURIComponent("Рецепт"));
  const targetK=Math.max(250,Math.min(650,leftK>900?leftK/2:leftK||450)),targetP=Math.max(15,Math.min(45,leftP>55?leftP/2:leftP||25));
  const picks=recipes.map(r=>({...r,score:Math.abs(r.calories-targetK)/4+Math.abs(r.protein-targetP)*3})).sort((a,b)=>a.score-b.score).slice(0,3);
  $("#smartText").textContent=`Осталось примерно ${fmt(leftK)} ккал и ${fmt(leftP)} г белка.`;
  $("#smartResult").innerHTML=picks.map(r=>`<div class="smart-line"><div class="emoji">${r.icon}</div><div class="grow"><b>${r.name}</b><small>${fmt(r.calories)} ккал · Б ${fmt(r.protein)} г · ${r.prep_time}</small></div><button data-pick="${r.id}">В рацион</button></div>`).join("");
  $$("[data-pick]").forEach(b=>b.onclick=()=>{const r=picks.find(x=>x.id===Number(b.dataset.pick));const p=new URLSearchParams({name:r.name,kcal:r.calories,p:r.protein,f:r.fat,c:r.carbs});location.href="/today?"+p.toString()})
}
$("#smartPick")?.addEventListener("click",smartPick);
window.addEventListener("planchange",()=>{fillGoals();if(getPlan()==="premium")loadWeek()});
fillGoals();if(getPlan()==="premium")loadWeek();
