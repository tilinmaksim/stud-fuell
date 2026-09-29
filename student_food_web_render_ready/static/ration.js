
const dateInput=$("#mealDate");
const today=()=>new Date().toISOString().slice(0,10);
dateInput.value=today();
$("#mealTime").value=new Date().toTimeString().slice(0,5);

let latestSums={calories:0,protein:0,fat:0,carbs:0};

function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}

function fillGoalInputs(){
  const g=getGoals();
  if($("#goalCalories")) $("#goalCalories").value=g.calories;
  if($("#goalProtein")) $("#goalProtein").value=g.protein;
  if($("#goalFat")) $("#goalFat").value=g.fat;
  if($("#goalCarbs")) $("#goalCarbs").value=g.carbs;
}
function updatePremiumProgress(){
  if(getPlan()!=="premium") return;
  const g=getGoals();
  const items=[
    ["Calories","calories","ккал"],
    ["Protein","protein","г"],
    ["Fat","fat","г"],
    ["Carbs","carbs","г"]
  ];
  for(const [suffix,key,unit] of items){
    const pct=Math.min(100,Math.round((latestSums[key]/Math.max(1,g[key]))*100));
    const prog=$("#prog"+suffix);
    const cap=$("#cap"+suffix);
    if(prog) prog.style.width=pct+"%";
    if(cap) cap.textContent=`${pct}% от цели ${fmt(g[key])} ${unit}`;
  }
}
async function loadMeals(){
  const rows=await api("/api/meals?date="+encodeURIComponent(dateInput.value));
  $("#countMeals").textContent=`${rows.length} приёмов`;
  latestSums=rows.reduce((a,r)=>({
    calories:a.calories+Number(r.calories||0),
    protein:a.protein+Number(r.protein||0),
    fat:a.fat+Number(r.fat||0),
    carbs:a.carbs+Number(r.carbs||0)
  }),{calories:0,protein:0,fat:0,carbs:0});

  $("#sumKcal").textContent=fmt(latestSums.calories);
  $("#sumP").textContent=fmt(latestSums.protein)+" г";
  $("#sumF").textContent=fmt(latestSums.fat)+" г";
  $("#sumC").textContent=fmt(latestSums.carbs)+" г";
  updatePremiumProgress();

  const l=$("#mealList");
  if(!rows.length){
    l.innerHTML='<div class="empty">На эту дату пока ничего нет.<br>Добавь первый приём пищи 👇</div>';
    return;
  }
  l.innerHTML=rows.map(r=>`<div class="meal-item">
    <div class="food-thumb">🍽️</div>
    <div class="item-main"><b>${esc(r.product_name)}</b>
    <div class="meta">⏰ ${r.meal_time} · ${fmt(r.calories)} ккал<br>Б ${fmt(r.protein)} · Ж ${fmt(r.fat)} · У ${fmt(r.carbs)}</div></div>
    <button class="danger" data-del="${r.id}">✕</button>
  </div>`).join("");
  $$("[data-del]").forEach(b=>b.onclick=async()=>{
    await api("/api/meals/"+b.dataset.del,{method:"DELETE"});
    toast("Запись удалена");
    loadMeals();
    if(getPlan()==="premium") loadWeekly();
  });
}

async function loadWeekly(){
  if(getPlan()!=="premium" || !$("#weekChart")) return;
  const end=new Date();
  const days=[];
  for(let i=6;i>=0;i--){
    const d=new Date(end);
    d.setDate(end.getDate()-i);
    const iso=d.toISOString().slice(0,10);
    const rows=await api("/api/meals?date="+encodeURIComponent(iso));
    const sum=rows.reduce((a,r)=>({
      calories:a.calories+Number(r.calories||0),
      protein:a.protein+Number(r.protein||0)
    }),{calories:0,protein:0});
    days.push({date:d,calories:sum.calories,protein:sum.protein,tracked:rows.length>0});
  }
  const tracked=days.filter(x=>x.tracked);
  const avgK=tracked.length?tracked.reduce((s,x)=>s+x.calories,0)/tracked.length:0;
  const avgP=tracked.length?tracked.reduce((s,x)=>s+x.protein,0)/tracked.length:0;
  $("#weekAvgKcal").textContent=fmt(avgK);
  $("#weekAvgProtein").textContent=fmt(avgP)+" г";
  $("#weekTracked").textContent=`${tracked.length}/7`;
  const goal=getGoals().calories;
  const labels=["Вс","Пн","Вт","Ср","Чт","Пт","Сб"];
  $("#weekChart").innerHTML=days.map(x=>{
    const h=Math.max(3,Math.min(100,(x.calories/Math.max(goal,1))*100));
    return `<div class="day-col"><div class="day-bar-wrap"><div class="day-bar" style="height:${h}%"></div></div><small>${labels[x.date.getDay()]}</small></div>`;
  }).join("");
}

$("#addMeal").onclick=async()=>{
  try{
    await api("/api/meals",{method:"POST",body:JSON.stringify({
      meal_date:dateInput.value,meal_time:$("#mealTime").value,product_name:$("#product").value,
      calories:$("#kcal").value||0,protein:$("#protein").value||0,fat:$("#fat").value||0,carbs:$("#carbs").value||0
    })});
    $("#product").value="";$("#kcal").value="";$("#protein").value="";$("#fat").value="";$("#carbs").value="";
    toast("Приём пищи сохранён");
    loadMeals();
    if(getPlan()==="premium") loadWeekly();
  }catch(e){toast(e.message)}
};

dateInput.onchange=loadMeals;
$("#todayBtn").onclick=()=>{dateInput.value=today();loadMeals()};

if($("#saveGoals")) $("#saveGoals").onclick=()=>{
  const goals={
    calories:Number($("#goalCalories").value)||2400,
    protein:Number($("#goalProtein").value)||150,
    fat:Number($("#goalFat").value)||80,
    carbs:Number($("#goalCarbs").value)||300
  };
  saveGoals(goals);
  toast("Цели сохранены");
  updatePremiumProgress();
  loadWeekly();
};

const params=new URLSearchParams(location.search);
if(params.get("name")){
  $("#product").value=params.get("name")||"";
  $("#kcal").value=params.get("kcal")||"";
  $("#protein").value=params.get("p")||"";
  $("#fat").value=params.get("f")||"";
  $("#carbs").value=params.get("c")||"";
  setTimeout(()=>toast("Данные из базы добавлены в форму"),250)
}

window.addEventListener("planchange",()=>{
  fillGoalInputs();
  updatePremiumProgress();
  if(getPlan()==="premium") loadWeekly();
  else{
    const caps=[["#capCalories","ккал за день"],["#capProtein","в рационе"],["#capFat","в рационе"],["#capCarbs","в рационе"]];
    caps.forEach(([s,t])=>{if($(s))$(s).textContent=t});
  }
});

fillGoalInputs();
loadMeals();
setTimeout(()=>{if(getPlan()==="premium")loadWeekly()},100);
