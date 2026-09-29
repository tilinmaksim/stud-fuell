
$("#nav").innerHTML=nav("reminders");$("#time").value="13:00";
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
async function load(){
  const rows=await api("/api/reminders?client_id="+encodeURIComponent(cid()));$("#remCount").textContent=`${rows.length} шт.`;const l=$("#remList");
  if(!rows.length){l.innerHTML='<div class="empty">Напоминаний пока нет.</div>';return}
  l.innerHTML=rows.map(r=>`<div class="item"><div class="item-icon">${r.title.toLowerCase().includes("завт")?"☕":r.title.toLowerCase().includes("уж")?"🌙":"⏰"}</div><div class="item-main"><b>${esc(r.title)}</b><div class="meta">${r.reminder_time}</div></div><button class="switch ${r.enabled?"on":""}" data-toggle="${r.id}" data-enabled="${r.enabled}"></button><button class="del" data-del="${r.id}">✕</button></div>`).join("");
  $$("[data-toggle]").forEach(b=>b.onclick=async()=>{await api("/api/reminders/"+b.dataset.toggle,{method:"PATCH",body:JSON.stringify({client_id:cid(),enabled:b.dataset.enabled!=="1"})});load()});
  $$("[data-del]").forEach(b=>b.onclick=async()=>{await api(`/api/reminders/${b.dataset.del}?client_id=${encodeURIComponent(cid())}`,{method:"DELETE"});toast("Удалено");load()})
}
$("#addReminder").onclick=async()=>{try{await api("/api/reminders",{method:"POST",body:JSON.stringify({client_id:cid(),title:$("#title").value,reminder_time:$("#time").value})});$("#title").value="";if("Notification" in window&&Notification.permission==="default")Notification.requestPermission();toast("Напоминание сохранено");load()}catch(e){toast(e.message)}};
load();
