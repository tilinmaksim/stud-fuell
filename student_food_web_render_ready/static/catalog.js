
let currentKind="Все",currentRows=[],selected=null;
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}

async function loadCatalog(){
  const q=$("#search").value.trim();
  currentRows=await api(`/api/catalog?kind=${encodeURIComponent(currentKind)}&q=${encodeURIComponent(q)}`);
  $("#catalogCount").textContent=`${currentRows.length} позиций`;
  $("#catalogGrid").innerHTML=currentRows.map(r=>`<button class="catalog-card" data-id="${r.id}">
    <div class="catalog-art">${r.icon||"🥗"}</div>
    <div class="catalog-body"><b>${esc(r.name)}</b><div class="desc">${esc(r.description.split("\n")[0])}</div>
    <span class="kind">${r.kind}</span><div class="foot"><span>${fmt(r.calories)} ккал</span><span>${r.prep_time}</span></div></div>
  </button>`).join("");
  $$("[data-id]").forEach(x=>x.onclick=()=>openDetail(Number(x.dataset.id)));
}

function openDetail(id){
  selected=currentRows.find(r=>r.id===id);
  if(!selected)return;
  $("#dKind").textContent=selected.kind;
  $("#dName").textContent=selected.name;
  $("#dIcon").textContent=selected.icon||"🥗";
  $("#dPrice").textContent=selected.price;
  $("#dTime").textContent="⏱ "+selected.prep_time;
  $("#dK").textContent=fmt(selected.calories);
  $("#dP").textContent=fmt(selected.protein)+" г";
  $("#dF").textContent=fmt(selected.fat)+" г";
  $("#dC").textContent=fmt(selected.carbs)+" г";
  $("#dDesc").textContent=selected.description;
  $("#detail").classList.add("open");
}
$("#closeDetail").onclick=()=>$("#detail").classList.remove("open");
$("#detail").onclick=e=>{if(e.target===$("#detail"))$("#detail").classList.remove("open")};
$("#search").oninput=loadCatalog;
$$(".filter").forEach(b=>b.onclick=()=>{
  $$(".filter").forEach(x=>x.classList.remove("active"));
  b.classList.add("active");
  currentKind=b.dataset.kind;
  loadCatalog();
});
$("#addFromCatalog").onclick=()=>{
  if(!selected)return;
  addRecipeToForm(selected);
};
function addRecipeToForm(r){
  const p=new URLSearchParams({name:r.name,kcal:r.calories,p:r.protein,f:r.fat,c:r.carbs});
  location.href="/ration?"+p.toString();
}

async function smartPick(){
  if(getPlan()!=="premium") return;
  const goals=getGoals();
  const today=new Date().toISOString().slice(0,10);
  const meals=await api("/api/meals?date="+today);
  const used=meals.reduce((a,r)=>({
    calories:a.calories+Number(r.calories||0),
    protein:a.protein+Number(r.protein||0)
  }),{calories:0,protein:0});
  const recipes=await api("/api/catalog?kind="+encodeURIComponent("Рецепт"));
  const remainK=Math.max(0,goals.calories-used.calories);
  const remainP=Math.max(0,goals.protein-used.protein);

  const mealTargetK=Math.max(250,Math.min(700,remainK/Math.max(1,remainK>900?2:1)));
  const mealTargetP=Math.max(15,Math.min(45,remainP/Math.max(1,remainP>55?2:1)));

  const ranked=recipes.map(r=>{
    const score=Math.abs(Number(r.calories)-mealTargetK)/4 + Math.abs(Number(r.protein)-mealTargetP)*3;
    return {...r,score};
  }).sort((a,b)=>a.score-b.score).slice(0,3);

  $("#smartText").textContent=`Сегодня осталось примерно ${fmt(remainK)} ккал и ${fmt(remainP)} г белка. Вот несколько спокойных вариантов из базы:`;
  $("#smartResults").innerHTML=ranked.map(r=>`<div class="smart-item">
    <div class="smart-icon">${r.icon||"🥗"}</div>
    <div class="smart-main"><b>${esc(r.name)}</b><small>${fmt(r.calories)} ккал · Б ${fmt(r.protein)} г · ${r.prep_time}</small></div>
    <button data-smart="${r.id}">В рацион</button>
  </div>`).join("");
  $$("[data-smart]").forEach(btn=>btn.onclick=()=>{
    const r=ranked.find(x=>x.id===Number(btn.dataset.smart));
    if(r)addRecipeToForm(r);
  });
}
if($("#smartPick")) $("#smartPick").onclick=smartPick;
window.addEventListener("planchange",()=>{
  if(getPlan()!=="premium" && $("#smartResults")) $("#smartResults").innerHTML="";
});
loadCatalog();
