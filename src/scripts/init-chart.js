import { Chart, registerables } from 'chart.js';
// Import the datalabels plugin
import ChartDataLabels from 'chartjs-plugin-datalabels';

// Register all Chart.js components
Chart.register(...registerables);
// Register the datalabels plugin
Chart.register(ChartDataLabels);

// Make Chart globally available for the other script
window.Chart = Chart;
// Make the plugin available globally as well (optional but good practice)
window.ChartDataLabels = ChartDataLabels;

console.log('Chart.js and DataLabels plugin initialized and registered.');

// Signal that Chart.js is ready
document.dispatchEvent(new CustomEvent('chartjs-ready'));
