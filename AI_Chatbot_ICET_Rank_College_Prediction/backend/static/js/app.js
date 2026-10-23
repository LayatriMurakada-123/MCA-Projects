async function post(url,data){
 const r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
 const d=await r.json(); if(!r.ok) throw Error(d.error||"Request failed"); return d;
}
function initPredictor(){
 const form=document.getElementById("predictForm");
 form.addEventListener("submit",async e=>{
  e.preventDefault();
  const data={score:document.getElementById("score").value,rank:document.getElementById("rank").value,
   category:document.getElementById("category").value,region:document.getElementById("region").value,
   course:document.getElementById("course").value,city:document.getElementById("city").value,max_fee:document.getElementById("max_fee").value};
  const out=document.getElementById("result"); out.innerHTML="<h2>Thinking…</h2><p>Agents are processing your request.</p>";
  try{
   const d=await post("/api/predict",data);
   let html=`<h2>Prediction Result</h2><div class="rank-box">Estimated Rank Band<strong>${d.rank_info.estimated_rank_band}</strong><small>Rank used for college matching: ${d.rank_used}</small></div><p>${d.explanation}</p>`;
   if(d.predictions.length) d.predictions.forEach(x=>html+=`<div class="prediction"><span class="badge">${x.chance} • ${x.confidence}%</span><h3>${x.name}</h3><div>${x.city} • ${x.region} • ${x.course}</div><small>Approx. cutoff: ${x.cutoff_rank} | Fee: ₹${Number(x.annual_fee).toLocaleString()}<br>${x.preference_reasons}</small></div>`);
   else html+="<p>No matching colleges found.</p>";
   out.innerHTML=html;
  }catch(err){out.innerHTML=`<h2>Error</h2><p>${err.message}</p>`}
 });
}
function initChat(){
 const form=document.getElementById("chatForm"), input=document.getElementById("chatInput"), box=document.getElementById("messages");
 form.addEventListener("submit",async e=>{e.preventDefault();sendChat(input.value)});
 window.quick=(text)=>{input.value=text;sendChat(text)};
 async function sendChat(text){
  if(!text.trim())return;
  box.innerHTML+=`<div class="user msg">${escapeHtml(text)}</div>`;input.value="";
  try{const d=await post("/api/chat",{message:text});box.innerHTML+=`<div class="bot msg">${escapeHtml(d.reply)}</div>`}
  catch(e){box.innerHTML+=`<div class="bot msg">Sorry, I couldn't process that.</div>`}
  box.scrollTop=box.scrollHeight;
 }
}
function escapeHtml(s){return s.replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
async function loadColleges(){
 const body=document.getElementById("collegeBody"), r=await fetch("/api/colleges"), rows=await r.json();
 body.innerHTML=rows.map(x=>`<tr><td><b>${x.name}</b><br><small>${x.university}</small></td><td>${x.city}</td><td>${x.region}</td><td>${x.course}</td><td>${x.cutoff_rank}</td><td>₹${Number(x.annual_fee).toLocaleString()}</td></tr>`).join("");
}
