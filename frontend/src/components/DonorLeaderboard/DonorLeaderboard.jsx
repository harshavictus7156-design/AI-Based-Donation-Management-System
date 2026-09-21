import { FiAward, FiRefreshCw } from "react-icons/fi";
import { useRanking } from "../../context/RankingContext";
import "./DonorLeaderboard.css";

const placementLabel = (rank) => {
  if (rank === 1) return "1st";
  if (rank === 2) return "2nd";
  if (rank === 3) return "3rd";
  return `#${rank}`;
};

export default function DonorLeaderboard({ showCurrentRank = false, detailed = false }) {
  const { rankings, currentDonor, loading, error, refreshRankings } = useRanking();

  return (
    <section className="donor-ranking-section" aria-labelledby="donor-ranking-title">
      <div className="donor-ranking-header">
        <div>
          <span>COMMUNITY IMPACT</span>
          <h2 id="donor-ranking-title">Donor leaderboard</h2>
        </div>
        <button className="donor-ranking-refresh" type="button" onClick={refreshRankings} title="Refresh donor rankings" aria-label="Refresh donor rankings">
          <FiRefreshCw />
        </button>
      </div>

      {showCurrentRank && currentDonor && (
        <div className={`current-donor-rank ${currentDonor.rank === 1 ? "top-rank-card" : ""}`}>
          <FiAward aria-hidden="true" />
          <div>
            <span>{currentDonor.rank === 1 ? "TOP DONOR" : "YOUR RANKING"}</span>
            <strong>{currentDonor.rank === 1 ? "#1" : `#${currentDonor.rank}`}</strong>
          </div>
          <div className="current-donor-rank-details">
            <span>{currentDonor.total_donation} items contributed</span>
            <span>{currentDonor.donation_count} completed donations</span>
          </div>
        </div>
      )}

      {detailed && !loading && rankings[0] && (
        <section className="top-donor-card" aria-label="Top donor">
          <FiAward aria-hidden="true" />
          <div>
            <span>TOP DONOR</span>
            <h3>{rankings[0].donor_name}</h3>
            <p>#1 with {rankings[0].total_donation} items contributed across {rankings[0].donation_count} completed donations.</p>
          </div>
        </section>
      )}

      <div className="donor-ranking-card">
        {loading ? (
          <p className="donor-ranking-message">Loading donor rankings...</p>
        ) : error ? (
          <div className="donor-ranking-message donor-ranking-error">
            <span>Unable to load donor rankings.</span>
            <button type="button" onClick={refreshRankings}>Try again</button>
          </div>
        ) : rankings.length === 0 ? (
          <p className="donor-ranking-message">No donor rankings available yet.</p>
        ) : (
          <div className="donor-ranking-list">
            {rankings.map((donor) => (
              <div className={`donor-ranking-row rank-${donor.rank} ${detailed && donor.donor_id === currentDonor?.donor_id ? "donor-ranking-current" : ""}`} key={donor.donor_id}>
                <span className="donor-ranking-rank">{placementLabel(donor.rank)}</span>
                <strong className="donor-ranking-user">{donor.donor_name}</strong>
                <span className="donor-ranking-total">{donor.total_donation} items</span>
                <span className="donor-ranking-count">{donor.donation_count} donations</span>
                {detailed && donor.donor_id === currentDonor?.donor_id && <span className="donor-ranking-you">You</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
