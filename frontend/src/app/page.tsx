import { ArrowDown, BarChart3, Flag } from "lucide-react";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import PredictionTable from "@/components/PredictionTable";
import { fetchFeatureImportance, fetchLatestPredictions } from "@/lib/api";
import type { PredictionsResponse } from "@/lib/types";

type Feature = { name: string; value: number };

export default async function HomePage() {
  const [forecast, rawFeatures]: [PredictionsResponse, (Feature | null)[]] =
    await Promise.all([fetchLatestPredictions(), fetchFeatureImportance()]);

  const features = rawFeatures.filter(
    (feature): feature is Feature => feature !== null,
  );

  return (
    <div className="dashboard-shell">
      <a className="skip-link" href="#predictions">Skip to predictions</a>

      <header className="topbar">
        <a className="brand" href="#predictions" aria-label="AK Predicts home">
          <span className="brand-mark">AK</span>
          <span className="brand-name">AK<span>_predicts</span></span>
        </a>
        <nav className="primary-nav" aria-label="Dashboard sections">
          <a href="#predictions">Predictions</a>
          <a href="#importance">Feature importance</a>
        </nav>
        <span className="model-status"><i aria-hidden="true" /> Model online</span>
      </header>

      <main>
        <section className="page-intro" aria-labelledby="page-title">
          <div>
            <p className="eyebrow"><Flag size={13} /> 2026 race forecast</p>
            <h1 id="page-title">The grid, decoded.</h1>
            <p className="intro-copy">One model. One finishing order. Every signal exposed.</p>
          </div>
          <a className="jump-link" href="#importance">See what drives the model <ArrowDown size={15} /></a>
        </section>

        <section id="predictions" className="content-section" aria-labelledby="predictions-title">
          <div className="section-header">
            <div>
              <p className="section-index">01 / Predictions</p>
              <h2 id="predictions-title">Predicted classification</h2>
            </div>
            <div className="dataset-meta">
              <span>{forecast.race || "Latest forecast"}</span>
              <strong>{forecast.total_rows} drivers</strong>
            </div>
          </div>
          <div className="data-surface"><PredictionTable rows={forecast.rows} /></div>
        </section>

        <section id="importance" className="content-section importance-section" aria-labelledby="importance-title">
          <div className="section-header">
            <div>
              <p className="section-index">02 / Model</p>
              <h2 id="importance-title">Feature importance</h2>
            </div>
            <div className="section-icon" aria-hidden="true"><BarChart3 size={19} /></div>
          </div>
          <FeatureImportanceChart features={features} />
        </section>
      </main>
    </div>
  );
}
