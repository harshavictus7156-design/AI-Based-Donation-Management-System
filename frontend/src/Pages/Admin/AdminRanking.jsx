import { useEffect, useMemo, useState } from "react";
import { FiRefreshCw, FiSearch } from "react-icons/fi";
import api from "../../services/api";
import "./AdminRanking.css";

const medal = { 1: "🥇", 2: "🥈", 3: "🥉" };

export default function AdminRanking() {
  const [rankings, setRankings] = useState([]);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("rank");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRankings = async () => {
    try {
      setLoading(true);
      setError("");
      const { data } = await api.get("donors/ranking/");
      setRankings(Array.isArray(data) ? data : data?.rankings || []);
    } catch (requestError) {
      setRankings([]);
      setError(requestError.response?.status === 403
        ? "You do not have permission to view donor rankings."
        : requestError.response?.status === 401
          ? "Your admin session has expired. Please sign in again."
          : "Unable to load donor rankings.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings();
  }, []);

  const visibleRankings = useMemo(() => {
    const query = search.trim().toLowerCase();
    return rankings
      .filter((donor) => !query || String(donor.donor_name || "").toLowerCase().includes(query))
      .sort((first, second) => sort === "name"
        ? String(first.donor_name).localeCompare(String(second.donor_name))
        : Number(first.rank) - Number(second.rank));
  }, [rankings, search, sort]);

  return (
    <div className="admin-ranking-page">
      <header className="admin-ranking-header">
        <div>
          <span className="admin-ranking-eyebrow">COMMUNITY IMPACT</span>
          <h1>Donor Ranking</h1>
          <p>Top donors based on donation contribution</p>
        </div>
        <button className="admin-ranking-refresh" type="button" onClick={fetchRankings} disabled={loading}>
          <FiRefreshCw aria-hidden="true" /> Refresh
        </button>
      </header>

      {!loading && !error && rankings.length > 0 && (
        <div className="admin-ranking-highlights">
          {rankings.slice(0, 3).map((donor) => (
            <article className={`admin-ranking-highlight rank-${donor.rank}`} key={donor.donor_id}>
              <span>{medal[donor.rank] || `#${donor.rank}`}</span>
              <div><strong>{donor.donor_name}</strong><small>{donor.total_quantity ?? donor.total_donation} items · {donor.donation_count} donations</small></div>
            </article>
          ))}
        </div>
      )}

      <div className="admin-ranking-toolbar">
        <label className="admin-ranking-search"><FiSearch aria-hidden="true" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search donor" aria-label="Search donor" /></label>
        <select value={sort} onChange={(event) => setSort(event.target.value)} aria-label="Sort ranking">
          <option value="rank">Ranking order</option>
          <option value="name">Donor name</option>
        </select>
      </div>

      {loading ? <div className="admin-ranking-state">Loading ranking...</div> : error ? (
        <div className="admin-ranking-state admin-ranking-error"><p>{error}</p><button type="button" onClick={fetchRankings}>Refresh</button></div>
      ) : visibleRankings.length === 0 ? <div className="admin-ranking-state">No donor ranking data available.</div> : (
        <div className="admin-ranking-table-wrap">
          <table className="admin-ranking-table">
            <thead><tr><th>Rank</th><th>Donor</th><th>Total donations</th><th>Total quantity</th><th>Status</th></tr></thead>
            <tbody>{visibleRankings.map((donor) => <tr key={donor.donor_id}>
              <td className="admin-ranking-rank">{medal[donor.rank] || `#${donor.rank}`}</td>
              <td><strong>{donor.donor_name}</strong><small>ID #{donor.donor_id}</small></td>
              <td>{donor.donation_count}</td>
              <td><strong>{donor.total_quantity ?? donor.total_donation}</strong></td>
              <td><span className="admin-ranking-status">{donor.status || "Active"}</span></td>
            </tr>)}</tbody>
          </table>
        </div>
      )}
    </div>
  );
}
