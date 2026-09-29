
$("#nav").innerHTML=nav("catalog");
let kind="Все",rows=[],selected=null;
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
async function load(){
  rows=await api(`/api/catalog?kind=${encodeURIComponent(kind)}&q=${encodeURIComponent($("#search").value.trim())}`);
  $("#count").textContent=`${rows.length} позиций`;
  $("#grid").innerHTML=rows.map(r=>`<button class="product" data-id="${r.id}"><div class="product-art">${r.icon}</div><div class="product-body"><b>${esc(r.name)}</b><p>${esc(r.description.split("\\n")[0])}</p><span class="tag">${r.tag}</span><div class="product-foot"><span>${fmt(r.calories)} ккал</span><span>${r.price}</span></div></div></button>`).join("");
  $$("[data-id]").forEach(x=>x.onclick=()=>open(Number(x.dataset.id)))
}
function open(id){
  selected=rows.find(r=>r.id===id);if(!selected)return;
  $("#dKind").textContent=selected.kind;$("#dName").textContent=selected.name;$("#dIcon").textContent=selected.icon;$("#dPrice").textContent=selected.price;$("#dTime").textContent="⏱ "+selected.prep_time;$("#dK").textContent=fmt(selected.calories);$("#dP").textContent=fmt(selected.protein)+" г";$("#dF").textContent=fmt(selected.fat)+" г";$("#dC").textContent=fmt(selected.carbs)+" г";$("#dDesc").textContent=selected.description;$("#modal").classList.add("open")
}
$("#closeModal").onclick=()=>$("#modal").classList.remove("open");$("#modal").onclick=e=>{if(e.target===$("#modal"))$("#modal").classList.remove("open")};
$("#search").oninput=load;$$(".filter").forEach(b=>b.onclick=()=>{$$(".filter").forEach(x=>x.classList.remove("active"));b.classList.add("active");kind=b.dataset.kind;load()});
$("#addFromCatalog").onclick=()=>{if(!selected)return;const p=new URLSearchParams({name:selected.name,kcal:selected.calories,p:selected.protein,f:selected.fat,c:selected.carbs});location.href="/today?"+p.toString()};
load();
