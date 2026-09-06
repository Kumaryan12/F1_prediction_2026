"use client";
import Link from "next/link";
import { RotateCcw } from "lucide-react";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return <main className="error-page"><Link className="footer-brand" href="/">AK_predicts</Link><span className="eyebrow">A QUICK PIT STOP</span><h1>The forecast<br />is taking a moment.</h1><p>We couldn’t load the prediction data. Please try again shortly.</p><button className="button button-red" onClick={reset}><RotateCcw size={16} />Try again</button></main>;
}
