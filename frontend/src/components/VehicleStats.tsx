import type { VehicleStatistics } from "../types/api";

interface VehicleStatsProps {
  stats: VehicleStatistics;
  totalLabel?: string;
  totalValue?: number;
}

function VehicleStats({ stats, totalLabel = "Total", totalValue }: VehicleStatsProps) {
  const total = totalValue ?? stats.car + stats.motorcycle + stats.bus + stats.truck;

  return (
    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
      <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
        <strong>Cars</strong>
        <div>{stats.car}</div>
      </div>
      <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
        <strong>Motorcycles</strong>
        <div>{stats.motorcycle}</div>
      </div>
      <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
        <strong>Buses</strong>
        <div>{stats.bus}</div>
      </div>
      <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
        <strong>Trucks</strong>
        <div>{stats.truck}</div>
      </div>
      <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
        <strong>{totalLabel}</strong>
        <div>{total}</div>
      </div>
    </div>
  );
}

export default VehicleStats;
