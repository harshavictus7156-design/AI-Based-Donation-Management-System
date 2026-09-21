import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import DonorLeaderboard from "../../components/DonorLeaderboard/DonorLeaderboard";
import "./NGODashboard.css";

export default function NGODashboard(){
 const navigate=useNavigate(); const [data,setData]=useState({donations:[],requirements:[],pickups:[]}); const [loading,setLoading]=useState(true);
 useEffect(()=>{(async()=>{try{const [d,r,p]=await Promise.all([api.get("ngo/donations/"),api.get("ngo/requirements/"),api.get("pickup/ngo/")]);const arr=x=>Array.isArray(x)?x:x?.results||x?.donations||x?.requirements||x?.pickups||[];setData({donations:arr(d.data),requirements:arr(r.data),pickups:arr(p.data)})}catch(e){console.error("NGO dashboard load error",e)}finally{setLoading(false)}})()},[]);
 const donations=data.donations; const count=s=>donations.filter(x=>x.status===s).length; const name=localStorage.getItem("user_name")||"NGO";
 if(loading)return <div className="ngo-clean-loading">Loading your NGO overview...</div>;
 return <div className="ngo-dashboard-clean">
  <div className="ngo-clean-welcome"><span>NGO WORKSPACE</span><h2>Welcome, {name} 👋</h2><p>A quick overview of your organization's current donation activity.</p></div>
  <div className="ngo-clean-stats">
   <article><b>📥</b><div><small>Pending Donations</small><strong>{count("Pending")}</strong></div></article>
   <article><b>✅</b><div><small>Accepted</small><strong>{count("Accepted")}</strong></div></article>
   <article><b>🚚</b><div><small>Collected</small><strong>{count("Collected")}</strong></div></article>
   <article><b>🎯</b><div><small>Active Requirements</small><strong>{data.requirements.length}</strong></div></article>
  </div>
  <div className="ngo-clean-actions"><div><span>QUICK ACTIONS</span><h3>What would you like to manage?</h3></div><div className="ngo-action-row"><button onClick={()=>navigate("/ngo-donations")}>📦 Review Donations</button><button onClick={()=>navigate("/ngo-requirements")}>➕ Add Requirement</button></div></div>
  <div className="ngo-clean-mini"><div><span>AT A GLANCE</span><h3>Current activity</h3></div><div className="ngo-mini-grid"><div><strong>{data.pickups.length}</strong><small>Pickup requests</small></div><div><strong>{donations.length}</strong><small>Total donations</small></div><div><strong>{data.requirements.length}</strong><small>Requirements</small></div></div></div>
  <DonorLeaderboard />
 </div>
}
