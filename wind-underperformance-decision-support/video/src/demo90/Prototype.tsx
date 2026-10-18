import React from 'react';
import {useCurrentFrame} from 'remotion';
import {DATA, mwh, pct} from './data';
import {
  accountingParts, bandPoints, barCentre, columnPoints, COLUMN, eventWindow,
  grossColumn, methodBars, neighbourPoints, xTime, yEnergy, yPower, yShortfall,
} from './layouts';
import {
  AxisBase, AxisCategories, AxisY, Backdrop, BarRect, Caption, Eyebrow, Headline,
  Label, Note, SeriesDots, SeriesPath, Stage, Value,
} from './marks';
import {fade, hold, mix, mixRect, phase, stagger, type Point} from './motion';
import {HIGHLIGHT, INK, METHOD_COLOUR, PLOT, TURBINES, type TurbineName} from './theme';

/**
 * Motion-system prototype for the 90-second demo - 20 seconds.
 *
 * It demonstrates the four things the full film depends on:
 *   1. four compressed turbine lines expanding into the neighbour chart
 *   2. the neighbour chart crushing back down and collecting into a column
 *   3. that column resolving into the energy accounting and separating into
 *      its real components
 *   4. a complete bar morph from method A to method B
 *
 * Every mark is bound to a value in src/demo90/data/demo_data.json, which the
 * export script writes from outputs/tables/*.csv. There is no screenshot in
 * this composition and no chart is a raster image.
 *
 * Geometry interpolates. Published figures never do: each one fades in at its
 * verified value and is gone before a different value appears.
 */

export const PROTOTYPE_FRAMES = 600; // 20.0s at 30fps

const {neighbours, accounting, methods, event} = DATA;
const TURBINE_LIST = neighbours.turbines;

/** Blends two point lists that may contain gaps, keeping a gap a gap. */
const mixNullable = (
  a: (Point | null)[], b: (Point | null)[], t: number,
): (Point | null)[] =>
  a.map((pa, i) => {
    const pb = b[i] ?? null;
    if (pa === null || pb === null) return null;
    return {x: mix(pa.x, pb.x, t), y: mix(pa.y, pb.y, t)};
  });

export const MotionPrototype: React.FC = () => {
  const frame = useCurrentFrame();

  // --- beat progressions ---------------------------------------------------
  const expand = phase(frame, 12, 92);        // band -> neighbour chart
  const crush = phase(frame, 160, 212);      // neighbour chart -> band
  const collect = phase(frame, 208, 260);    // band -> packed column
  const solid = phase(frame, 256, 284);      // packed marks -> solid column
  const split = phase(frame, 332, 378);      // gross column -> its components
  const toBars = phase(frame, 432, 468);     // components -> turbine baseline
  const riseA = phase(frame, 462, 502);      // method A bars rise
  const crushA = phase(frame, 530, 554);     // method A bars crush down
  const riseB = phase(frame, 558, 586);      // method B bars rise

  // --- the records, moving between states ---------------------------------
  const seriesPoints = (turbine: TurbineName) => {
    let points = mixNullable(bandPoints(turbine), neighbourPoints(turbine), expand);
    points = mixNullable(points, bandPoints(turbine), crush);
    points = mixNullable(points, columnPoints(turbine), collect);
    return points;
  };

  const chartOpacity = (1 - collect) * (1 - solid * 0.0);
  const dotsOpacity = Math.min(collect, 1 - solid);
  const linesVisible = (1 - solid) * (1 - toBars);

  // --- the accounting column ----------------------------------------------
  const gross = grossColumn();
  const parts = accountingParts();
  const base = yEnergy(0);
  const reviewableHeight = base - yEnergy(accounting.reviewable);
  const nonPersistentHeight = base - yEnergy(accounting.nonPersistent);

  // At rest the two components stack exactly into the gross column; the export
  // asserts that they sum to it, so this separation is arithmetic, not a
  // drawing convention.
  const reviewableFrom = {
    x: COLUMN.x, y: base - reviewableHeight, width: COLUMN.width, height: reviewableHeight,
  };
  const nonPersistentFrom = {
    x: COLUMN.x, y: gross.y, width: COLUMN.width, height: nonPersistentHeight,
  };
  const reviewableRect = mixRect(reviewableFrom, parts[0].rect, split);
  const nonPersistentRect = mixRect(nonPersistentFrom, parts[1].rect, split);

  // The components flatten onto the baseline before the turbine bars grow out
  // of it, so the same ground is shared between the two charts.
  const flatten = (rect: typeof reviewableRect) =>
    mixRect(rect, {x: rect.x, y: yShortfall(0) - 3, width: rect.width, height: 3}, toBars);

  // --- the method comparison ----------------------------------------------
  const barsA = methodBars('A');
  const barsB = methodBars('B');
  const leaderA = methods.leaders.A;
  const leaderB = methods.leaders.B;

  const methodBarRect = (index: number) => {
    const a = barsA[index];
    const b = barsB[index];
    const baseline = {x: a.rect.x, y: yShortfall(0) - 3, width: a.rect.width, height: 3};
    const grown = mixRect(baseline, a.rect, stagger(riseA, index, barsA.length));
    const crushed = mixRect(grown, baseline, crushA);
    return mixRect(crushed, b.rect, stagger(riseB, index, barsB.length));
  };
  const showingB = frame >= 556;

  // --- copy timing ---------------------------------------------------------
  const conclusion = hold(frame, 96, 152);
  const evidence = hold(frame, 106, 152);
  const grossLabel = hold(frame, 288, 326);
  const partsLabel = hold(frame, 382, 424);
  const methodALabel = hold(frame, 498, 528);
  const methodBLabel = fade(frame, 580, 14);
  const eventRect = eventWindow();

  return (
    <Backdrop>
      <Stage>
        {/* Axes assemble before the marks resolve, and recede when they leave. */}
        <AxisY
          ticks={[0, 500, 1000, 1500, 2000]}
          scale={yPower}
          format={(v) => `${v}`}
          unit="Active power (kW)"
          opacity={Math.min(expand, 1 - crush)}
        />
        <AxisY
          ticks={[0, 200, 400, 600]}
          scale={yEnergy}
          format={(v) => `${v}`}
          unit="Potential shortfall (MWh)"
          opacity={Math.min(solid, 1 - toBars)}
        />
        <AxisY
          ticks={[0, 2, 4, 6]}
          scale={yShortfall}
          format={(v) => `${v}%`}
          unit={methods.metric}
          opacity={Math.min(riseA, 1)}
        />
        <AxisBase y={yPower(0)} opacity={Math.max(expand * (1 - crush), riseA)} />

        {/* The interval under investigation, shaded behind the series. */}
        <rect
          x={eventRect.x} y={eventRect.y} width={eventRect.width} height={eventRect.height}
          fill="rgba(226,160,93,0.08)"
          opacity={Math.min(fade(frame, 96, 16), 1 - crush)}
        />

        {/* The records themselves, in whichever state the film is in. */}
        {TURBINE_LIST.map((turbine) => {
          const points = seriesPoints(turbine);
          const isHost = turbine === neighbours.eventTurbine;
          return (
            <g key={turbine}>
              <SeriesPath
                id={turbine}
                points={points}
                colour={TURBINES[turbine]}
                width={isHost ? 4 : 2.4}
                opacity={chartOpacity * linesVisible * (isHost ? 1 : 0.85)}
                clipWidth={expand < 1 ? undefined : undefined}
              />
              <SeriesDots
                points={points}
                colour={TURBINES[turbine]}
                radius={2}
                opacity={dotsOpacity * 0.9}
              />
            </g>
          );
        })}

        {/* The gross column, then its components. */}
        <BarRect rect={gross} fill="#38506b"
          opacity={Math.min(solid, 1 - split) * (1 - toBars)} />
        <BarRect rect={flatten(reviewableRect)} fill={parts[0].fill}
          opacity={Math.min(split, 1)} />
        <BarRect rect={flatten(nonPersistentRect)} fill={parts[1].fill}
          opacity={Math.min(split, 1)} />
        <BarRect rect={parts[2].rect} fill="transparent" hatched
          opacity={Math.min(split, 1 - toBars)} />

        {/* The method comparison: one rect per turbine, keyed so each bar is
            the same machine before and after the morph. */}
        {TURBINE_LIST.map((turbine, i) => (
          <BarRect
            key={`bar-${turbine}`}
            rect={methodBarRect(i)}
            fill={showingB && turbine === leaderB ? METHOD_COLOUR.B
              : !showingB && turbine === leaderA ? HIGHLIGHT
                : '#49596d'}
            opacity={Math.min(riseA, 1)}
          />
        ))}
        <AxisCategories
          y={yShortfall(0)}
          opacity={Math.min(riseA, 1)}
          items={TURBINE_LIST.map((turbine, i) => ({
            key: turbine,
            x: barsA[i].rect.x + barsA[i].rect.width / 2,
            label: turbine,
            colour: (showingB ? turbine === leaderB : turbine === leaderA)
              ? INK.bright : INK.muted,
          }))}
        />

        {/* Published values. Each appears at its verified figure and leaves
            before a different figure is shown in its place. */}
        <Value
          x={COLUMN.x + COLUMN.width / 2} y={gross.y - 42}
          text={mwh(accounting.gross)} opacity={grossLabel * (1 - split)}
        />
        <Label
          x={COLUMN.x + COLUMN.width / 2} y={gross.y - 12}
          text="Gross apparent shortfall" opacity={grossLabel * (1 - split)}
        />

        <Value x={parts[0].rect.x + COLUMN.width / 2} y={parts[0].rect.y - 38}
          text={mwh(accounting.reviewable)} opacity={partsLabel} size={38} />
        <Label x={parts[0].rect.x + COLUMN.width / 2} y={parts[0].rect.y - 12}
          text="Reviewable events" opacity={partsLabel} size={20} />

        <Value x={parts[1].rect.x + COLUMN.width / 2} y={parts[1].rect.y - 38}
          text={mwh(accounting.nonPersistent)} opacity={partsLabel} size={38} />
        <Label x={parts[1].rect.x + COLUMN.width / 2} y={parts[1].rect.y - 12}
          text="Non-persistent" opacity={partsLabel} size={20} />

        <Value x={parts[2].rect.x + COLUMN.width / 2} y={parts[2].rect.y - 38}
          text="unknown" opacity={partsLabel} size={38} colour={INK.amber} />
        <Label x={parts[2].rect.x + COLUMN.width / 2} y={parts[2].rect.y - 12}
          text="Quantity unknown" opacity={partsLabel} size={20} />

        {/* Method callouts, anchored to the bar they describe. */}
        <Value
          x={barCentre(barsA[TURBINE_LIST.indexOf(leaderA)]).x}
          y={barCentre(barsA[TURBINE_LIST.indexOf(leaderA)]).y - 26}
          text={`Method A · ${leaderA} · ${pct(methods.byMethod.A[leaderA])}`}
          opacity={methodALabel} size={30} colour={INK.amber}
        />
        <Value
          x={barCentre(barsB[TURBINE_LIST.indexOf(leaderB)]).x}
          y={barCentre(barsB[TURBINE_LIST.indexOf(leaderB)]).y - 26}
          text={`Method B · ${leaderB} · ${pct(methods.byMethod.B[leaderB])}`}
          opacity={methodBLabel} size={30} colour="#7fb3e0"
        />
      </Stage>

      {/* --- screen copy ----------------------------------------------- */}
      <Eyebrow opacity={fade(frame, 6, 14)}>
        Wind underperformance &#183; decision support
      </Eyebrow>

      <Headline opacity={conclusion} lift={(1 - fade(frame, 96, 14)) * 14}>
        Investigate {event.turbine} first.
      </Headline>

      <div style={{
        position: 'absolute', left: PLOT.left, top: 172, display: 'flex', gap: 48,
        opacity: evidence, fontFamily: 'inherit',
      }}>
        {[
          {value: `${event.durationHours} h`, label: 'Continuous interval'},
          {value: `${event.mwhMin}–${event.mwhMax} MWh`, label: 'Potential shortfall'},
          {value: event.methodsAgreeing, label: 'Methods agreeing'},
        ].map((item) => (
          <div key={item.label}>
            <div style={{fontSize: 34, fontWeight: 720, color: INK.bright}}>{item.value}</div>
            <div style={{fontSize: 19, color: INK.muted, marginTop: 2}}>{item.label}</div>
          </div>
        ))}
      </div>

      <Caption opacity={hold(frame, 118, 154)}>
        Request operational records before diagnosing the cause.
      </Caption>
      <Caption opacity={hold(frame, 390, 428)}>
        Missing is unknown &#8212; not zero.
      </Caption>
      <Caption opacity={fade(frame, 566, 14)} tone={INK.bright}>
        Changing the reference changed the priority.
      </Caption>

      <Note opacity={hold(frame, 126, 154)}>
        Potential shortfall against a statistical reference &#8212; not confirmed
        recoverable energy.
      </Note>
      <Note opacity={hold(frame, 396, 428)}>
        The two components sum to the gross figure. The missing-data quantity is
        unknown and is drawn at a token height, not to scale.
      </Note>
      <Note opacity={fade(frame, 574, 14)}>
        Prioritisation, not diagnosis. No cause is established by either method.
      </Note>
    </Backdrop>
  );
};
