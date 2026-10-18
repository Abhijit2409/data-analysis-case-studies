import React from 'react';
import {useCurrentFrame} from 'remotion';
import {DATA, mwh, pct} from './data';
import {
  accountingParts, bandPoints, barCentre, benchmarkBars, burdenBand, columnPoints,
  COLUMN, evidenceCards, eventWindow, grossColumn, intervalMarks, methodBars,
  neighbourPoints, seasonBars, stripPoints, unknownToken, xTime, yEnergy, yLag,
  yPower, yRecovery, yShortfall,
} from './layouts';
import {
  AxisBase, AxisCategories, AxisY, Backdrop, BarRect, Caption, EvidenceCard,
  Eyebrow, Headline, Label, Note, SeriesDots, SeriesPath, SnapValue, Stage,
  UnknownToken, Value,
} from './marks';
import {fade, hold, mix, mixRect, phase, revealWidth, stagger, type Point} from './motion';
import {COPY, FILM_FRAMES, MOVE} from './timeline';
import {FONT, HIGHLIGHT, INK, METHOD_COLOUR, PLOT, TURBINES, type TurbineName} from './theme';

export {FILM_FRAMES};

/**
 * The 89-second hiring-manager demo.
 *
 * One continuous composition rather than a sequence of cuts: the same records
 * travel between every chart, so each transition is the same evidence being
 * reorganised rather than a new picture replacing an old one.
 *
 * Everything the viewer reads as a chart is SVG built from
 * src/demo90/data/demo_data.json, which the export writes from
 * outputs/tables/*.csv. No screenshot appears anywhere in this film.
 *
 * Geometry interpolates. Published figures never do - each appears at a
 * verified value, and where one figure replaces another it does so while the
 * text is invisible.
 */

const {neighbours, accounting, methods, event, timestamps, benchmark} = DATA;
const TURBINE_LIST = neighbours.turbines;

const mixNullable = (
  a: (Point | null)[], b: (Point | null)[], t: number,
): (Point | null)[] =>
  a.map((pa, i) => {
    const pb = b[i] ?? null;
    if (pa === null || pb === null) return null;
    return {x: mix(pa.x, pb.x, t), y: mix(pa.y, pb.y, t)};
  });

const span = (frame: number, window: readonly [number, number]) =>
  phase(frame, window[0], window[1]);

const copy = (frame: number, window: readonly number[]) =>
  window.length > 1 ? hold(frame, window[0], window[1]) : fade(frame, window[0]);

export const WindDemo90: React.FC = () => {
  const frame = useCurrentFrame();

  // --- geometry progressions ----------------------------------------------
  const expand = span(frame, MOVE.expand);
  const crush = span(frame, MOVE.crush);
  const collect = span(frame, MOVE.collect);
  const solidify = span(frame, MOVE.solidify);
  const disperse = span(frame, MOVE.disperse);
  const seasonsIn = span(frame, MOVE.seasonsIn);
  const correctSummer = span(frame, MOVE.correctSummer);
  const intervalsIn = span(frame, MOVE.intervalsIn);
  const intervalsClear = span(frame, MOVE.intervalsClear);
  const seasonsOut = span(frame, MOVE.seasonsOut);
  const regather = span(frame, MOVE.regather);
  const split = span(frame, MOVE.split);
  const unknownIn = span(frame, MOVE.unknownIn);
  const toBaseline = span(frame, MOVE.toBaseline);
  const riseA = span(frame, MOVE.riseA);
  const crushA = span(frame, MOVE.crushA);
  const riseB = span(frame, MOVE.riseB);
  const toBenchmark = span(frame, MOVE.toBenchmark);
  const burdenIn = span(frame, MOVE.burdenIn);
  const toSignals = span(frame, MOVE.toSignals);
  const rebuildChart = span(frame, MOVE.rebuildChart);
  const drawLines = span(frame, MOVE.drawLines);
  const toCards = span(frame, MOVE.toCards);

  // The compressed band opens out horizontally over the first second. After
  // that this is the identity transform and nothing else is affected.
  const openSpread = mix(3.2, 1, phase(frame, 0, 34));
  const bandMiddle = PLOT.top + PLOT.height / 2;

  // --- where the records are, at this frame -------------------------------
  const seriesPoints = (turbine: TurbineName) => {
    let p = mixNullable(bandPoints(turbine), neighbourPoints(turbine), expand);
    p = mixNullable(p, bandPoints(turbine), crush);
    p = mixNullable(p, columnPoints(turbine), collect);
    p = mixNullable(p, stripPoints(turbine), disperse);
    p = mixNullable(p, columnPoints(turbine), regather);
    p = mixNullable(p, bandPoints(turbine), toSignals);
    p = mixNullable(p, neighbourPoints(turbine), rebuildChart);
    return p;
  };

  // The records are a line while they describe power, and individual marks
  // while they are being counted, carried or regrouped.
  const lineDrawing = fade(frame, MOVE.drawLines[0], 8);
  const asLine = Math.max(
    (1 - collect) * (1 - solidify),
    lineDrawing * (1 - toCards),
  );
  const asMarks = Math.max(
    Math.min(collect, 1 - solidify),
    Math.min(disperse, 1 - seasonsIn),
    Math.min(regather * (1 - solidify), 1),
    Math.min(toSignals, 1 - rebuildChart),
    Math.min(rebuildChart, 1 - lineDrawing),
  ) * (1 - toCards);

  // --- the energy column and its components -------------------------------
  const gross = grossColumn();
  const parts = accountingParts();
  const token = unknownToken();
  const base = yEnergy(0);
  const reviewableHeight = base - yEnergy(accounting.reviewable);
  const nonPersistentHeight = base - yEnergy(accounting.nonPersistent);
  const reviewableFrom = {
    x: COLUMN.x, y: base - reviewableHeight, width: COLUMN.width, height: reviewableHeight,
  };
  const nonPersistentFrom = {
    x: COLUMN.x, y: gross.y, width: COLUMN.width, height: nonPersistentHeight,
  };
  const reviewableRect = mixRect(reviewableFrom, parts[0].rect, split);
  const nonPersistentRect = mixRect(nonPersistentFrom, parts[1].rect, split);
  const flatten = (rect: typeof reviewableRect) =>
    mixRect(rect, {x: rect.x, y: yShortfall(0) - 3, width: rect.width, height: 3}, toBaseline);

  // The gross column exists from when the marks solidify until it separates,
  // and again when the film returns to it.
  const columnAlive = Math.min(
    Math.max(solidify * (1 - disperse), regather),
    1 - split,
  ) * (1 - toBaseline);

  // --- seasonal alignment --------------------------------------------------
  const seasonsPublished = seasonBars(false);
  const seasonsCorrected = seasonBars(true);
  const seasonRect = (i: number) => {
    const from = seasonsPublished[i].rect;
    const to = seasonsCorrected[i].rect;
    const current = mixRect(from, to, correctSummer);
    const zero = yLag(0);
    const collapsed = {x: current.x, y: zero, width: current.width, height: 3};
    const grown = mixRect(collapsed, current, seasonsIn);
    return mixRect(grown, collapsed, seasonsOut);
  };
  const seasonsAlive = Math.min(seasonsIn, 1 - seasonsOut);

  // --- method comparison ---------------------------------------------------
  const barsA = methodBars('A');
  const barsB = methodBars('B');
  const leaderA = methods.leaders.A;
  const leaderB = methods.leaders.B;
  const methodBarRect = (index: number) => {
    const a = barsA[index];
    const baseline = {x: a.rect.x, y: yShortfall(0) - 3, width: a.rect.width, height: 3};
    const grown = mixRect(baseline, a.rect, stagger(riseA, index, barsA.length));
    const crushed = mixRect(grown, baseline, crushA);
    return mixRect(crushed, barsB[index].rect, stagger(riseB, index, barsB.length));
  };
  const showingB = frame >= MOVE.crushA[1];
  const methodAlive = Math.min(riseA, 1 - toBenchmark);

  // --- detection benchmark -------------------------------------------------
  const bench = benchmarkBars();
  const band = burdenBand();
  const benchRect = (i: number) => {
    const target = bench[i].rect;
    const source = barsB[Math.min(i + 1, barsB.length - 1)].rect;
    return mixRect(source, target, toBenchmark);
  };
  const benchAlive = Math.min(toBenchmark, 1 - toSignals);

  // --- evidence cards ------------------------------------------------------
  const cards = evidenceCards();

  return (
    <Backdrop>
      <Stage>
        {/* Axes, each present only while its own chart is. */}
        <AxisY ticks={[0, 500, 1000, 1500, 2000]} scale={yPower}
          format={(v) => `${v}`} unit="Active power (kW)"
          opacity={Math.max(Math.min(expand, 1 - crush), rebuildChart * (1 - toCards))} />
        <AxisY ticks={[0, 200, 400, 600]} scale={yEnergy}
          format={(v) => `${v}`} unit="Potential shortfall (MWh)"
          opacity={Math.min(columnAlive + split * (1 - toBaseline), 1)} />
        <AxisY ticks={[-2, -1, 0]} scale={yLag}
          format={(v) => `${v} h`} unit="Best lag against ERA5 reanalysis (hours)"
          opacity={seasonsAlive} />
        <AxisY ticks={[0, 2, 4, 6]} scale={yShortfall}
          format={(v) => `${v}%`} unit={methods.metric}
          opacity={methodAlive} />
        <AxisY ticks={[0, 0.5, 1]} scale={yRecovery}
          format={(v) => v.toFixed(1)} unit="Injected-event recovery rate"
          opacity={benchAlive} />
        <AxisBase y={yPower(0)}
          opacity={Math.max(Math.max(expand * (1 - crush), rebuildChart * (1 - toCards)),
            Math.max(methodAlive, benchAlive))} />

        {/* The interval under investigation. */}
        <rect x={eventWindow().x} y={eventWindow().y}
          width={eventWindow().width * Math.max(span(frame, MOVE.markEvent), rebuildChart)}
          height={eventWindow().height}
          fill="rgba(226,160,93,0.08)"
          opacity={Math.max(1 - crush, rebuildChart * (1 - toCards))} />
        <line x1={eventWindow().x} y1={eventWindow().y + eventWindow().height}
          x2={eventWindow().x + eventWindow().width * span(frame, MOVE.markEvent)}
          y2={eventWindow().y + eventWindow().height}
          stroke={INK.amber} strokeWidth={2.5}
          opacity={Math.min(span(frame, MOVE.markEvent), 1 - crush) * 0.8} />

        {/* The records. */}
        <g transform={`translate(0 ${bandMiddle}) scale(1 ${openSpread}) translate(0 ${-bandMiddle})`}>
        {TURBINE_LIST.map((turbine) => {
          const points = seriesPoints(turbine);
          const isHost = turbine === neighbours.eventTurbine;
          // In scene 7 the lines draw on from left to right. The whole series
          // is always in the path; only how much is uncovered changes.
          const reveal = frame >= MOVE.drawLines[0] && frame <= MOVE.toCards[0]
            ? revealWidth(drawLines, PLOT.width)
            : undefined;
          return (
            <g key={turbine}>
              <SeriesPath id={turbine} points={points} colour={TURBINES[turbine]}
                width={isHost ? 4 : 2.4}
                opacity={asLine * (isHost ? 1 : 0.85)}
                clipWidth={reveal} />
              <SeriesDots points={points} colour={TURBINES[turbine]} radius={2}
                opacity={asMarks * 0.9} />
            </g>
          );
        })}
        </g>

        {/* Gross column, then its components, then the unscaled unknown. */}
        <BarRect rect={gross} fill="#38506b" opacity={columnAlive} />
        {(() => {
          const sweep = phase(frame, 556, 646);
          const y = mix(yEnergy(0), gross.y, sweep);
          const alive = Math.min(fade(frame, 552, 14), 1 - fade(frame, 650, 12)) * columnAlive;
          return (
            <g opacity={alive}>
              <line x1={gross.x - 54} y1={y} x2={gross.x + gross.width + 54} y2={y}
                stroke={INK.amber} strokeWidth={2} strokeDasharray="9 7" />
              <text x={gross.x + gross.width + 66} y={y + 7}
                fill={INK.amber} fontSize={26} fontFamily={FONT}>?</text>
            </g>
          );
        })()}
        <BarRect rect={flatten(reviewableRect)} fill={parts[0].fill}
          opacity={Math.min(split, 1) * (1 - riseA)} />
        <BarRect rect={flatten(nonPersistentRect)} fill={parts[1].fill}
          opacity={Math.min(split, 1) * (1 - riseA)} />
        <UnknownToken rect={token.rect} breakX={token.breakX}
          breakTop={token.breakTop} breakBottom={token.breakBottom}
          opacity={Math.min(unknownIn, 1 - toBaseline)} />

        {/* Seasonal alignment. */}
        {seasonsPublished.map((bar, i) => (
          <BarRect key={bar.key} rect={seasonRect(i)} fill={bar.fill}
            opacity={seasonsAlive} />
        ))}
        <line x1={PLOT.left} y1={yLag(0)} x2={PLOT.left + PLOT.width} y2={yLag(0)}
          stroke={INK.faint} strokeWidth={1.5} opacity={seasonsAlive} />

        {/* Duplicate and absent intervals, one mark each, leaving one by one. */}
        {([0, 1] as const).map((row) =>
          intervalMarks(row).map((mark) => {
            const out = stagger(intervalsClear, mark.index, 48, 0.8);
            return (
              <rect key={mark.key} x={mark.x} y={mark.y + out * -26}
                width={mark.size} height={mark.size} rx={2}
                fill={row === 0 ? '#2f6ea8' : '#b5651d'}
                opacity={Math.min(intervalsIn, 1) * (1 - out)} />
            );
          }))}

        {/* Method comparison. */}
        {TURBINE_LIST.map((turbine, i) => (
          <BarRect key={`bar-${turbine}`} rect={methodBarRect(i)}
            fill={showingB && turbine === leaderB ? METHOD_COLOUR.B
              : !showingB && turbine === leaderA ? HIGHLIGHT : '#49596d'}
            opacity={methodAlive} />
        ))}
        <AxisCategories y={yShortfall(0)} opacity={methodAlive}
          items={TURBINE_LIST.map((turbine, i) => ({
            key: turbine, x: barsA[i].rect.x + barsA[i].rect.width / 2, label: turbine,
            colour: (showingB ? turbine === leaderB : turbine === leaderA)
              ? INK.bright : INK.muted,
          }))} />

        {/* Detection benchmark, and the burden that reframes it. */}
        {bench.map((bar, i) => (
          <BarRect key={`bench-${bar.key}`} rect={benchRect(i)} fill={bar.fill}
            opacity={benchAlive} />
        ))}
        <g opacity={Math.min(burdenIn, benchAlive)}>
          <rect x={band.x} y={band.y} width={band.width} height={band.height}
            fill="rgba(226,160,93,0.14)" />
          <line x1={band.x} y1={band.y} x2={band.x + band.width} y2={band.y}
            stroke={INK.amber} strokeWidth={2.5} strokeDasharray="12 8" />
        </g>
        <AxisCategories y={yRecovery(0)} opacity={benchAlive}
          items={bench.map((bar) => ({
            key: bar.key, x: bar.rect.x + bar.rect.width / 2,
            label: bar.key === 'B' ? 'B · decision method' : 'C · challenger',
            colour: bar.key === 'C' ? INK.amber : INK.muted,
          }))} />

        {/* Operational evidence. */}
        {cards.map((card, i) => (
          <EvidenceCard key={card.key} rect={card.rect} label={card.label}
            opacity={stagger(toCards, i, cards.length) * (1 - fade(frame, 2620, 20))}
            lift={(1 - stagger(toCards, i, cards.length)) * 30} />
        ))}

        {/* --- published values ------------------------------------------ */}
        <Value x={COLUMN.x + COLUMN.width / 2} y={gross.y - 42}
          text={mwh(accounting.gross)}
          opacity={Math.max(copy(frame, COPY.grossLabel), copy(frame, COPY.grossAgain))
            * (1 - split)} />
        <Label x={COLUMN.x + COLUMN.width / 2} y={gross.y - 12}
          text="Gross apparent shortfall"
          opacity={Math.max(copy(frame, COPY.grossLabel), copy(frame, COPY.grossAgain))
            * (1 - split)} />

        <Value x={parts[0].rect.x + COLUMN.width / 2} y={parts[0].rect.y - 38}
          text={mwh(accounting.reviewable)} opacity={copy(frame, COPY.partsLabel)} size={40} />
        <Label x={parts[0].rect.x + COLUMN.width / 2} y={parts[0].rect.y - 12}
          text="Inside reviewable events" opacity={copy(frame, COPY.partsLabel)} size={21} />
        <Value x={parts[1].rect.x + COLUMN.width / 2} y={parts[1].rect.y - 38}
          text={mwh(accounting.nonPersistent)} opacity={copy(frame, COPY.partsLabel)} size={40} />
        <Label x={parts[1].rect.x + COLUMN.width / 2} y={parts[1].rect.y - 12}
          text="Outside that scope" opacity={copy(frame, COPY.partsLabel)} size={21} />
        <Value x={token.rect.x + token.rect.width / 2} y={token.rect.y + 52}
          text="unknown" opacity={copy(frame, COPY.partsLabel)} size={42} colour={INK.amber} />
        <Label x={token.rect.x + token.rect.width / 2} y={token.rect.y + 86}
          text="Quantity unknown" opacity={copy(frame, COPY.partsLabel)} size={20}
          colour={INK.amber} />
        <Label x={token.rect.x + token.rect.width / 2} y={token.rect.y + token.rect.height + 30}
          text="not plotted to scale" opacity={copy(frame, COPY.partsLabel)} size={19} />

        {/* Seasonal lags. Winter never moves; summer snaps to its corrected
            value while the text is invisible, so no intermediate is shown. */}
        <Value x={seasonsPublished[0].rect.x + 95} y={seasonRect(0).y + seasonRect(0).height + 46}
          text={`${timestamps.winterBefore} h`} size={40}
          opacity={Math.max(copy(frame, COPY.publishedLags), copy(frame, COPY.correctedLags))} />
        <Label x={seasonsPublished[0].rect.x + 95} y={seasonRect(0).y + seasonRect(0).height + 76}
          text="Winter (Nov-Feb)" size={21}
          opacity={Math.max(copy(frame, COPY.publishedLags), copy(frame, COPY.correctedLags))} />
        <SnapValue frame={frame} switchAt={COPY.summerSnap}
          x={seasonsPublished[1].rect.x + 95} y={seasonRect(1).y + seasonRect(1).height + 46}
          before={`${timestamps.summerBefore} h`} after={`${timestamps.summerAfter} h`}
          size={40}
          opacity={Math.max(copy(frame, COPY.publishedLags), copy(frame, COPY.correctedLags))} />
        <Label x={seasonsPublished[1].rect.x + 95} y={seasonRect(1).y + seasonRect(1).height + 76}
          text="Summer (May-Aug)" size={21}
          opacity={Math.max(copy(frame, COPY.publishedLags), copy(frame, COPY.correctedLags))} />

        {/* Interval counts. */}
        {([0, 1] as const).map((row) => {
          const marks = intervalMarks(row);
          const first = marks[0];
          const label = row === 0 ? 'Duplicate intervals' : 'Absent intervals';
          const before = row === 0 ? timestamps.duplicatesBefore : timestamps.absentBefore;
          const after = row === 0 ? timestamps.duplicatesAfter : timestamps.absentAfter;
          return (
            <g key={`count-${row}`}>
              <Label x={first.x} y={first.y - 22} text={label} anchor="start" size={21}
                opacity={copy(frame, COPY.intervalLabels)} />
              <SnapValue frame={frame} switchAt={MOVE.intervalsClear[1] + 2}
                x={first.x + 500} y={first.y + 14} anchor="end"
                before={`${before}`} after={`${after}`} size={44}
                colour={row === 0 ? '#7fb3e0' : INK.amber}
                opacity={copy(frame, COPY.intervalLabels)} />
            </g>
          );
        })}

        {/* Method callouts. */}
        <Value x={barCentre(barsA[TURBINE_LIST.indexOf(leaderA)]).x}
          y={barCentre(barsA[TURBINE_LIST.indexOf(leaderA)]).y - 30}
          text={`Method A · ${leaderA} · ${pct(methods.byMethod.A[leaderA])}`}
          opacity={copy(frame, COPY.methodALabel)} size={32} colour={HIGHLIGHT} />
        <Value x={barCentre(barsB[TURBINE_LIST.indexOf(leaderB)]).x}
          y={barCentre(barsB[TURBINE_LIST.indexOf(leaderB)]).y - 30}
          text={`Method B · ${leaderB} · ${pct(methods.byMethod.B[leaderB])}`}
          opacity={copy(frame, COPY.methodBLabel)} size={32} colour="#7fb3e0" />

        {/* Benchmark values. */}
        <Value x={bench[0].rect.x + bench[0].rect.width / 2} y={bench[0].rect.y - 30}
          text={benchmark.recovery.B.toFixed(3)} size={40}
          opacity={copy(frame, COPY.recoveryLabels)} />
        <Value x={bench[1].rect.x + bench[1].rect.width / 2} y={bench[1].rect.y - 30}
          text={benchmark.recovery.C.toFixed(3)} size={40} colour={INK.amber}
          opacity={copy(frame, COPY.recoveryLabels)} />
        <Value x={band.x + band.width + 30} y={band.y + 12} anchor="start"
          text={`${benchmark.burdenPct.C.toFixed(1)}%`} size={38} colour={INK.amber}
          opacity={copy(frame, COPY.burdenLabel)} />
        <Label x={band.x + band.width + 30} y={band.y + 42} anchor="start"
          text="Alert burden on untouched windows" size={20} colour={INK.amber}
          opacity={copy(frame, COPY.burdenLabel)} />

        {/* Event evidence. */}
        <g opacity={copy(frame, COPY.eventStats)}>
          {[
            {v: `${event.durationHours} h`, l: 'Continuous interval'},
            {v: `${neighbours.recordsInsideEvent}`, l: 'Consecutive event records'},
            {v: pct(neighbours.pctAtOrBelowZero), l: `${neighbours.eventTurbine} at or below zero`},
            {v: `${neighbours.neighboursProducingPct.toFixed(0)}%`, l: 'All three neighbours producing'},
          ].map((item, i) => (
            <g key={item.l}>
              <Value x={PLOT.left + 30 + i * 370} y={PLOT.top + PLOT.height + 34}
                text={item.v} anchor="start" size={38} opacity={1} />
              <Label x={PLOT.left + 30 + i * 370} y={PLOT.top + PLOT.height + 62}
                text={item.l} anchor="start" size={19} opacity={1} />
            </g>
          ))}
        </g>
      </Stage>

      {/* --- screen copy ------------------------------------------------- */}
      <Eyebrow opacity={copy(frame, COPY.eyebrow)}>
        Wind underperformance &#183; decision support
      </Eyebrow>

      <Headline opacity={copy(frame, COPY.conclusion)}
        lift={(1 - fade(frame, COPY.conclusion[0], 14)) * 14}>
        Investigate {event.turbine} first.
      </Headline>

      <div style={{
        position: 'absolute', left: PLOT.left, top: 176, display: 'flex', gap: 58,
      }}>
        {[
          {value: `${event.durationHours} hours`, label: 'Continuous interval'},
          {value: `${event.mwhMin}–${event.mwhMax} MWh`, label: 'Potential shortfall'},
          {value: `Methods ${event.methodsAgreeing.split('+').join(' + ')} agree`, label: 'Independent methods'},
        ].map((item, index) => (
          <div key={item.label} style={{
            opacity: hold(frame, COPY.evidenceRow[0] + index * 26, COPY.evidenceRow[1]),
          }}>
            <div style={{fontSize: 34, fontWeight: 720, color: INK.bright}}>{item.value}</div>
            <div style={{fontSize: 19, color: INK.muted, marginTop: 3}}>{item.label}</div>
          </div>
        ))}
      </div>

      <Caption opacity={copy(frame, COPY.action)}>
        Request operational records before diagnosing the cause.
      </Caption>
      <Caption opacity={copy(frame, COPY.question)}>
        How much is trustworthy and decision-relevant?
      </Caption>
      <Caption opacity={copy(frame, COPY.trustCaption)}>
        The timestamps looked valid. They were still wrong.
      </Caption>
      <Caption opacity={copy(frame, COPY.scopeCaption)}>
        Missing is unknown &#8212; not zero.
      </Caption>
      <Caption opacity={copy(frame, COPY.methodCaption)}>
        Changing the reference changed the priority.
      </Caption>
      <Caption opacity={copy(frame, COPY.modelCaption)}>
        The model improved.
      </Caption>
      <Caption opacity={copy(frame, COPY.modelVerdict)} tone={INK.amber}>
        I still would not deploy it.
      </Caption>
      <Caption opacity={copy(frame, COPY.eventCaption)}>
        All three methods flag the same interval.
      </Caption>
      <Caption opacity={copy(frame, COPY.causeUnknown)} tone={INK.amber}>
        Cause: unknown.
      </Caption>

      <Note opacity={copy(frame, COPY.action)}>
        Potential shortfall against a statistical reference &#8212; not confirmed
        recoverable energy.
      </Note>
      <Note opacity={copy(frame, COPY.correctedLags)}>
        The seasonal inconsistency is removed. Both seasons still sit one hour
        behind &#8212; the absolute lag does not become zero.
      </Note>
      <Note opacity={copy(frame, COPY.scopeCaption)}>
        Potential shortfall is not confirmed recoverable energy. The missing
        quantity is unknown and is not plotted to scale.
      </Note>
      <Note opacity={copy(frame, COPY.julyNote)}>
        Remove the July event and {leaderB} falls below {leaderA}. Prioritisation,
        not diagnosis.
      </Note>
      <Note opacity={copy(frame, COPY.burdenLabel)}>
        Roughly two in five untouched windows would raise an alert. The
        improvement does not support an automated operating decision.
      </Note>
      <Note opacity={copy(frame, COPY.causeUnknown)}>
        Neighbouring operation corroborates that wind was available. It does not
        establish the cause, nor identical conditions at each turbine.
      </Note>

      {/* Closing. */}
      <div style={{
        position: 'absolute', left: PLOT.left, right: 230, bottom: 96,
        opacity: copy(frame, COPY.cards),
        fontSize: 48, fontWeight: 700, color: INK.bright, letterSpacing: -1,
      }}>
        Investigate first. <span style={{color: INK.amber}}>Diagnose only with evidence.</span>
      </div>

      <div style={{
        position: 'absolute', left: PLOT.left, right: 230, top: 300,
        opacity: copy(frame, COPY.closing), textAlign: 'center',
      }}>
        <div style={{fontSize: 74, fontWeight: 750, color: INK.bright, letterSpacing: -2}}>
          Wind Underperformance Decision Support
        </div>
        <div style={{height: 26}} />
        <div style={{fontSize: 36, fontWeight: 620, color: INK.amber}}>
          Validate &#8594; Quantify &#8594; Challenge &#8594; Investigate
        </div>
        <div style={{height: 46}} />
        <div style={{fontSize: 21, lineHeight: 1.6, color: INK.muted}}>
          Independent portfolio case study &#183; Public ENGIE La Haute Borne data
          &#183; Etalab Open Licence 2.0 &#183; via OpenOA
          <br />
          Not Clir Renewables software, data or methodology.
        </div>
      </div>
    </Backdrop>
  );
};
