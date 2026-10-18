import raw from './data/demo_data.json';
import type {TurbineName} from './theme';

/**
 * Typed access to the exported repository data.
 *
 * Every chart in the demo reads its marks from here, so a mark cannot exist
 * without a value behind it. The export script that writes this file reads only
 * outputs/tables/*.csv.
 */

export type SeriesPoint = {t: number; p: number | null};

export const DATA = raw as unknown as {
  source: string;
  neighbours: {
    turbines: TurbineName[];
    eventTurbine: TurbineName;
    series: Record<TurbineName, SeriesPoint[]>;
    /** Observations drawn across the whole displayed window, per turbine. */
    contextObservations: number;
    contextObservationsPerTurbine: Record<string, number>;
    /** Observations inside the highlighted event only, per turbine. */
    eventObservationsPerTurbine: Record<string, number>;
    totalMinutes: number;
    eventStartMinutes: number;
    eventEndMinutes: number;
    maxPower: number;
    recordsInsideEvent: number;
    pctAtOrBelowZero: number;
    neighboursProducingPct: number;
    missingRecordsInWindow: number;
    meanPower: Record<string, number>;
  };
  accounting: {
    gross: number;
    reviewable: number;
    nonPersistent: number;
    missingIsUnknown: boolean;
    missingBasis: string;
  };
  methods: {
    byMethod: Record<'A' | 'B' | 'C', Record<TurbineName, number>>;
    leaders: Record<'A' | 'B' | 'C', TurbineName>;
    turbines: TurbineName[];
    metric: string;
  };
  event: {
    turbine: TurbineName;
    durationHours: number;
    mwhMin: number;
    mwhMax: number;
    methodsAgreeing: string;
    confidence: string;
    recordsRequired: string[];
  };
  timestamps: {
    winterBefore: number; summerBefore: number;
    winterAfter: number; summerAfter: number;
    duplicatesBefore: number; duplicatesAfter: number;
    absentBefore: number; absentAfter: number;
    countsStatedInSource: boolean;
    differenceRemoved: boolean;
  };
  benchmark: {
    recovery: Record<'A' | 'B' | 'C', number>;
    burdenPct: Record<'A' | 'B' | 'C', number>;
    windowsTested: number;
    basis: string;
  };
};

/** Formats a published figure for display. Never used mid-transition. */
export const mwh = (value: number) => `${value.toFixed(1)} MWh`;
export const pct = (value: number) => `${value.toFixed(2)}%`;
