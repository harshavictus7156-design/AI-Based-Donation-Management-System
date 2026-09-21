import DonorLeaderboard from "../../components/DonorLeaderboard/DonorLeaderboard";
import "./RankingPage.css";

export default function RankingPage({ showCurrentRank = false }) {
  return (
    <div className="ranking-page">
      <section className="ranking-page-intro">
        <span>COMMUNITY IMPACT</span>
        <h2>Donor Ranking</h2>
        <p>See the donors making the biggest impact in our community.</p>
      </section>

      <DonorLeaderboard showCurrentRank={showCurrentRank} detailed />
    </div>
  );
}
