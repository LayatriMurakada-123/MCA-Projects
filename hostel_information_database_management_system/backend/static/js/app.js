async function api(url, options={}) {
  const res = await fetch("/api/" + url, {
    headers: {"Content-Type":"application/json"},
    ...options
  });
  const data = await res.json();
  if(!res.ok) throw new Error(data.error || "Request failed");
  return data;
}
function toast(msg, error=false){
  const el=document.getElementById("toast");
  el.textContent=msg; el.style.cssText=`position:fixed;right:20px;bottom:20px;background:${error?"#b91c1c":"#166534"};color:#fff;padding:12px 18px;border-radius:8px;z-index:99`;
  setTimeout(()=>el.style.display="none",2500);
}
function openModal(){document.getElementById("modal").classList.add("open")}
function closeModal(){document.getElementById("modal").classList.remove("open")}
async function loadDashboard(){
  const d=await api("dashboard");
  document.getElementById("studentsCount").textContent=d.students;
  document.getElementById("roomsCount").textContent=d.rooms;
  document.getElementById("availableRooms").textContent=d.available_rooms;
  document.getElementById("pendingComplaints").textContent=d.pending_complaints;
  document.getElementById("paidFees").textContent="₹"+Number(d.paid_fees).toLocaleString();
  document.getElementById("totalFees").textContent="₹"+Number(d.total_fees).toLocaleString();
}
const configs={
 students:{cols:["id","name","email","phone","course","year","room_number"], action:"student"},
 rooms:{cols:["id","room_number","block","floor","capacity","occupied","available","type"], action:"room"},
 staff:{cols:["id","name","role","phone","email","shift"], action:"staff"},
 fees:{cols:["id","student_name","amount","due_date","paid_date","status","description"], action:"fee"},
 complaints:{cols:["id","student_name","title","description","status","created_at"], action:"complaint"}
};
async function setupPage(type){
  const cfg=configs[type];
  await loadTable(type,cfg);
  if(type==="students") await loadRoomOptions();
  document.getElementById("dataForm").addEventListener("submit", async e=>{
    e.preventDefault();
    const obj=Object.fromEntries(new FormData(e.target).entries());
    try{
      await api(type,{method:"POST",body:JSON.stringify(obj)});
      closeModal(); e.target.reset(); toast("Saved successfully"); await loadTable(type,cfg);
      if(type==="students") await loadRoomOptions();
    }catch(err){toast(err.message,true)}
  });
}
async function loadTable(type,cfg){
  const rows=await api(type);
  const body=document.querySelector(`#${type}Table tbody`);
  body.innerHTML=rows.length?rows.map(r=>{
    let vals=cfg.cols.map(c=>{
      let v=r[c]??"—";
      if(c==="amount") v="₹"+Number(v).toLocaleString();
      if(c==="status") v=`<span class="status">${v}</span>`;
      return `<td>${v}</td>`;
    }).join("");
    let act=`<button class="danger" onclick="removeItem('${type}',${r.id})">Delete</button>`;
    if(type==="rooms" && r.occupied>0) act="<span>Occupied</span>";
    return `<tr>${vals}<td>${act}</td></tr>`;
  }).join(""):`<tr><td colspan="${cfg.cols.length+1}" class="empty">No records found</td></tr>`;
}
async function removeItem(type,id){
  if(!confirm("Are you sure you want to delete this record?"))return;
  try{await api(`${type}/${id}`,{method:"DELETE"});toast("Deleted");await loadTable(type,configs[type])}
  catch(e){toast(e.message,true)}
}
async function loadRoomOptions(){
  const rooms=await api("rooms");
  const sel=document.getElementById("roomSelect");
  if(!sel)return;
  sel.innerHTML='<option value="">No room</option>'+rooms.filter(r=>r.available>0).map(r=>`<option value="${r.id}">${r.room_number} (${r.available} available)</option>`).join("");
}
