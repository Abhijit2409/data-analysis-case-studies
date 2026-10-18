import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {
  Callout, Camera, Cursor, Environment, LowerThird, Ring, ScreenLabel, ScreenPanel,
  Scrim, Spotlight, StatStrip, Statement, between, centre, drive, focusOn,
  type Framing, type Shot,
} from './components/Film';
import {MONTAGE, TILE} from './grid';
import {bar, box, clicked, fitHeight, pad, union} from './screens';
import {FONT_STACK, LAYOUT, LIGHT, TEXT} from './theme';

/**
 * The full 42-second product film.
 *
 * Every panel is a photograph of the running Streamlit application. The camera
 * moves; the application does not. Where a figure appears in overlay copy or a
 * callout it is checked against the repository by
 * scripts/v2/verify_v2_claims.py - a callout may only restate what the element
 * it points at already shows.
 *
 * Nothing here invents a control, a page, a state or an interaction. The two
 * clicks in the film are clicks that were really performed against the running
 * application during capture.
 */

const W = 1050;              // every panel is drawn this wide
const CLOSE_TILE = 326;      // montage tile width, sized to clear the frame edge
const fit = (cropW: number) => fitHeight(cropW);

// Scene boundaries, in frames at 30fps.
export const SCENES = {
  open: {from: 0, duration: 120},        // 0.0 - 4.0
  trust: {from: 120, duration: 180},     // 4.0 - 10.0
  scope: {from: 300, duration: 180},     // 10.0 - 16.0
  method: {from: 480, duration: 240},    // 16.0 - 24.0
  event: {from: 720, duration: 270},     // 24.0 - 33.0
  decide: {from: 990, duration: 150},    // 33.0 - 38.0
  close: {from: 1140, duration: 120},    // 38.0 - 42.0
} as const;

export const FILM_FRAMES = 1260;         // 42.0s

// --- framings --------------------------------------------------------------

const COCKPIT: Framing = {screen: 'cockpit', x: 0, w: 1440, y: 0, h: fit(1440)};
const ACCOUNTING: Framing = {screen: 'cockpit', x: 360, w: 1020, y: 560, h: fit(1020)};
const RANKING: Framing = {screen: 'cockpit', x: 858, w: 522, y: 782, h: fit(522)};
const LAG: Framing = {screen: 'datatrust', x: 906, w: 492, y: 700, h: fit(492)};
const EXPANDER_CROP = {x: 386, w: 470, y: 1560, h: 700};
const CLOSED: Framing = {screen: 'datatrust', ...EXPANDER_CROP};
const EXPANDED: Framing = {screen: 'datatrust_expander', ...EXPANDER_CROP};
const EVENT: Framing = {screen: 'explorer', x: 370, w: 1004, y: 1838, h: fit(1004)};
const EVIDENCE: Framing = {screen: 'explorer', x: 370, w: 1004, y: 2200, h: fit(1004)};

const ease = (frame: number, at: number, length = 14) =>
  interpolate(frame, [at, at + length], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** A statement that appears, holds, and leaves before the next one arrives. */
const hold = (frame: number, inAt: number, outAt: number) =>
  Math.min(ease(frame, inAt), 1 - ease(frame, outAt, 10));

// --- Scene 1: cinematic product opening (0.0 - 4.0) ------------------------

const Open: React.FC = () => {
  const frame = useCurrentFrame();

  // The application is on screen from the first frame; only its depth and the
  // camera angle change, so nothing opens on an empty frame.
  const arrive = drive(frame, [0, 46], [0.42, 1]);
  const shot: Shot = {
    zoom: drive(frame, [0, 120], [0.99, 1.1]),
    x: 0,
    y: drive(frame, [0, 120], [34, -18]),
    rotateY: drive(frame, [0, 120], [-12, -4]),
    rotateX: drive(frame, [0, 120], [4, 1]),
  };

  return (
    <>
      <Camera shot={shot}>
        <div style={{opacity: arrive, transform: `translateZ(${(1 - arrive) * -420}px)`}}>
          <ScreenPanel frame={COCKPIT} width={W}>
            <Ring box={pad(union(box('cockpit', 'gross'), box('cockpit', 'missing')), 18, 14)}
              opacity={ease(frame, 58)} />
          </ScreenPanel>
        </div>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={ease(frame, 20)}>Executive cockpit</ScreenLabel>
      <Statement opacity={hold(frame, 22, 64)} lift={(1 - ease(frame, 22)) * 16}>
        671.6 MWh
        <br />apparent shortfall.
      </Statement>
      <Statement opacity={ease(frame, 76)} lift={(1 - ease(frame, 76)) * 16}>
        How much
        <br />
        <span style={{color: TEXT.amber}}>can I trust?</span>
      </Statement>
    </>
  );
};

// --- Scene 2: data trust (4.0 - 10.0) --------------------------------------

/**
 * The cursor opens the timestamp explanation - a click really performed during
 * capture - and the camera travels from the seasonal-alignment chart down to
 * the paragraph that states the duplicate and absent interval counts.
 *
 * The chart shows winter -1 h and summer -2 h before correction and both at
 * -1 h after. What goes to zero is the difference between the seasons, never
 * the lag itself, so no overlay here says otherwise.
 */
const CLICK = 110;

const DataTrust: React.FC = () => {
  const frame = useCurrentFrame();
  const expander = clicked('datatrust_expander');
  const atControl = frame >= 84;
  const opened = frame >= CLICK;

  // Beat one: the seasonal-alignment chart. Beat two: the control that reveals
  // the interval counts, clicked for real during capture.
  const chartShot: Shot = {
    zoom: drive(frame, [0, 84], [1.0, 1.08]), x: 0, y: 0,
    rotateY: drive(frame, [0, 84], [7, 3]), rotateX: 2,
  };
  // The panel is taller than the frame here, so the camera travels down it:
  // the control first, then the paragraph the click reveals.
  const readShot = between(frame, [84, 176],
    {zoom: 1.0, x: 0, y: 54, rotateY: -6, rotateX: 2},
    {zoom: 1.02, x: 0, y: -148, rotateY: -1, rotateX: 1});

  const travel = drive(frame, [88, CLICK - 6], [0, 1]);
  const from = {x: expander.x + 300, y: expander.y + 230};
  const to = {x: expander.x - 16, y: expander.y + 4};

  return (
    <>
      {!atControl ? (
        <Camera shot={chartShot}>
          <ScreenPanel frame={LAG} width={W}>
            <Ring box={pad(box('datatrust', 'timestampChart'), 10, 8)}
              opacity={ease(frame, 18) * 0.6} />
          </ScreenPanel>
        </Camera>
      ) : (
        <Camera shot={readShot}>
          <ScreenPanel frame={opened ? EXPANDED : CLOSED} width={W}>
            {opened ? (
              <>
                <Ring box={pad(box('datatrust_expander', 'explanation'), 12, 10)}
                  opacity={ease(frame, CLICK + 14) * 0.8} />
                <Callout box={box('datatrust_expander', 'explanation')}
                  opacity={ease(frame, CLICK + 26)} size={14} side="above" offset={14}>
                  48 &#8594; 0 duplicate &#183; 48 &#8594; 0 absent
                </Callout>
              </>
            ) : null}
            <Cursor
              x={from.x + (to.x - from.x) * travel}
              y={from.y + (to.y - from.y) * travel}
              opacity={ease(frame, 86, 8) * (1 - ease(frame, CLICK + 22, 10))}
              press={interpolate(frame, [CLICK - 8, CLICK + 6], [0, 1],
                {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
            />
          </ScreenPanel>
        </Camera>
      )}

      <Scrim />
      <ScreenLabel opacity={ease(frame, 10)}>
        Data trust &#183; {atControl ? 'timestamp correction' : 'seasonal alignment'}
      </ScreenLabel>
      <Statement opacity={hold(frame, 14, 70)} lift={(1 - ease(frame, 14)) * 16}>
        The timestamps
        <br />looked valid.
      </Statement>
      <Statement opacity={ease(frame, CLICK + 24)} lift={(1 - ease(frame, CLICK + 24)) * 16}>
        They were
        <br />
        <span style={{color: TEXT.amber}}>still wrong.</span>
      </Statement>
      <LowerThird opacity={hold(frame, 30, 76)}>
        Winter lagged one hour and summer two against ERA5. After correction both
        sit at one hour &#8212; the seasonal difference is gone.
      </LowerThird>
      <LowerThird opacity={ease(frame, CLICK + 40)}>
        Corrected before any performance figure was computed. It is not the cause
        of what follows.
      </LowerThird>
    </>
  );
};

// --- Scene 3: scope the apparent shortfall (10.0 - 16.0) -------------------

const Scope: React.FC = () => {
  const frame = useCurrentFrame();

  const shot = between(frame, [0, 170],
    {zoom: 1.0, x: 0, y: 14, rotateY: -7, rotateX: 2},
    {zoom: 1.0, x: 0, y: -18, rotateY: -2, rotateX: 1});

  // Each figure is ringed in turn, then the unknown one is isolated. The
  // application supplies every number; the camera only decides the order.
  const steps = [
    {key: 'gross', at: 16},
    {key: 'reviewable', at: 44},
    {key: 'nonPersistent', at: 72},
  ] as const;

  return (
    <>
      <Camera shot={shot}>
        <ScreenPanel frame={ACCOUNTING} width={W}>
          {steps.map((step) => (
            <Ring key={step.key} box={pad(box('cockpit', step.key), 12, 10)}
              opacity={Math.min(ease(frame, step.at, 10), 1 - ease(frame, 104, 12)) * 0.9}
              colour={LIGHT.blue} />
          ))}
          <Spotlight box={pad(box('cockpit', 'missing'), 16, 12)}
            opacity={ease(frame, 108, 16)} scrim={0.56} />
        </ScreenPanel>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={ease(frame, 8)}>
        Executive cockpit &#183; 2015 energy accounting
      </ScreenLabel>
      <Statement opacity={ease(frame, 112)} lift={(1 - ease(frame, 112)) * 16}>
        Missing is unknown
        <br />
        <span style={{color: TEXT.amber}}>&#8212; not zero.</span>
      </Statement>
      <LowerThird opacity={hold(frame, 24, 104)}>
        671.6 MWh gross &#183; 380.8 MWh inside reviewable events &#183; 290.8 MWh
        outside the persistence rule.
      </LowerThird>
      <LowerThird opacity={ease(frame, 140)}>
        Potential shortfall against a statistical reference &#8212; not confirmed
        recoverable energy.
      </LowerThird>
    </>
  );
};

// --- Scene 4: challenge the reference method (16.0 - 24.0) -----------------

/**
 * The chart is the real grouped comparison and is never re-sorted. Attention
 * moves between two bars that are already there: under A the tallest is
 * R80790, under B it is R80711. The callouts restate the values the chart's own
 * axis shows.
 */
const Method: React.FC = () => {
  const frame = useCurrentFrame();
  const barA = bar('cockpit', 'A', 'R80790');
  const barB = bar('cockpit', 'B', 'R80711');

  const wide = focusOn({at: centre(box('cockpit', 'rankingChart')),
    crop: RANKING, width: W, zoom: 1.0, rotateY: 8, rotateX: 2});
  const onA = focusOn({at: {x: barA.x + barA.w / 2, y: barA.y + 70},
    crop: RANKING, width: W, zoom: 1.3, rotateY: 3, rotateX: 1});
  const onB = focusOn({at: {x: barB.x + barB.w / 2, y: barB.y + 70},
    crop: RANKING, width: W, zoom: 1.3, rotateY: -3, rotateX: 1});

  const shot = frame < 96
    ? between(frame, [10, 90], wide, onA)
    : frame < 170
      ? between(frame, [96, 160], onA, onB)
      : between(frame, [170, 240], onB, {...wide, zoom: 1.04});

  // Callout text in capture pixels: the panel is drawn at W/522 times capture
  // scale, so 15 here reads at roughly 30px on screen.
  const SIZE = 15;

  return (
    <>
      <Camera shot={shot}>
        <ScreenPanel frame={RANKING} width={W}>
          <Spotlight box={pad(barA, 10, 6)} opacity={hold(frame, 52, 104)} scrim={0.5} radius={4} />
          <Callout box={barA} opacity={hold(frame, 58, 104)} size={SIZE} offset={16}>
            Method A &#183; R80790 &#183; 6.15%
          </Callout>

          <Spotlight box={pad(barB, 10, 6)} opacity={hold(frame, 118, 182)}
            scrim={0.5} radius={4} ring={LIGHT.blue} />
          <Callout box={barB} opacity={hold(frame, 124, 182)} size={SIZE} offset={16}
            tone={LIGHT.blue}>
            Method B &#183; R80711 &#183; 5.35%
          </Callout>
        </ScreenPanel>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={ease(frame, 8)}>
        Executive cockpit &#183; shortfall per turbine
      </ScreenLabel>
      <Statement opacity={ease(frame, 188)} lift={(1 - ease(frame, 188)) * 16}>
        Changing the reference
        <br />changed the priority.
      </Statement>
      <LowerThird opacity={ease(frame, 206)}>
        Gross potential shortfall &#8212; not confirmed loss. Prioritisation, not
        diagnosis.
      </LowerThird>
    </>
  );
};

// --- Scene 5: investigate the event (24.0 - 33.0) --------------------------

/**
 * The camera travels from the cockpit to the Investigation explorer with both
 * on screen, then pushes into the neighbour comparison. The chart is drawn by
 * the application from the exported table: gaps stay gaps and no line is
 * bridged across a missing value.
 */
const ROOM_GAP = 170;
const ROOM_SHIFT = (ROOM_GAP + W) / 2;

const Event: React.FC = () => {
  const frame = useCurrentFrame();

  const atCockpit: Shot = {zoom: 1.04, x: ROOM_SHIFT * 1.04, y: 0, rotateY: 6, rotateX: 1};
  const atEvent: Shot = {zoom: 1.0, x: -ROOM_SHIFT, y: 0, rotateY: -5, rotateX: 1};
  const pushed: Shot = {zoom: 1.2, x: -ROOM_SHIFT * 1.2, y: -52, rotateY: -1, rotateX: 1};

  const shot = frame < 46
    ? between(frame, [0, 46], atCockpit, atEvent)
    : between(frame, [46, 150], atEvent, pushed);

  return (
    <>
      <Camera shot={shot}>
        <div style={{display: 'flex', alignItems: 'center', gap: ROOM_GAP}}>
          <ScreenPanel frame={RANKING} width={W} dim={drive(frame, [0, 54], [0, 0.5])} />
          <ScreenPanel frame={EVENT} width={W} />
        </div>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={ease(frame, 40)}>
        Investigation explorer &#183; R80711 &#183; 26&#8211;28 July 2015
      </ScreenLabel>

      <StatStrip
        opacity={hold(frame, 64, 150)}
        lift={(1 - ease(frame, 64)) * 14}
        items={[
          {value: '42.5 h', label: 'Continuous interval'},
          {value: '255', label: 'Consecutive records'},
          {value: '97.65%', label: 'R80711 at or below zero'},
          {value: '100%', label: 'All three neighbours producing'},
        ]}
      />

      <Statement opacity={hold(frame, 70, 156)} lift={(1 - ease(frame, 70)) * 16}>
        All three methods flag
        <br />the same interval.
      </Statement>
      <Statement opacity={hold(frame, 164, 226)} lift={(1 - ease(frame, 164)) * 16}>
        Cause:
        <br /><span style={{color: TEXT.amber}}>unknown.</span>
      </Statement>
      <Statement opacity={ease(frame, 240)} lift={(1 - ease(frame, 240)) * 16} size={46}>
        Remove this event and R80711
        <br />falls below R80790.
      </Statement>
      <LowerThird opacity={hold(frame, 96, 226)}>
        Neighbouring production confirms simultaneous peer operation; it does not
        identify the cause. Gaps are records with no value &#8212; never zero.
      </LowerThird>
    </>
  );
};

// --- Scene 6: decision support (33.0 - 38.0) -------------------------------

const Decide: React.FC = () => {
  const frame = useCurrentFrame();

  const wide: Shot = {zoom: 1.0, x: 0, y: 10, rotateY: -6, rotateX: 2};
  const onRecords = focusOn({at: {x: 1100, y: 2600},
    crop: EVIDENCE, width: W, zoom: 1.46, rotateY: -1, rotateX: 1});
  const shot = between(frame, [8, 110], wide, onRecords);

  return (
    <>
      <Camera shot={shot}>
        <ScreenPanel frame={EVIDENCE} width={W}>
          <Ring box={pad(union(box('explorer', 'recordsRequired'),
            {...box('explorer', 'nextAction'), h: 2}), 16, 12)}
            opacity={ease(frame, 54) * 0.9} />
          <Callout box={box('explorer', 'recordsRequired')}
            opacity={ease(frame, 70)} size={17} side="above" offset={16}>
            Required &#183; not available
          </Callout>
        </ScreenPanel>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={ease(frame, 8)}>
        Investigation explorer &#183; operational evidence
      </ScreenLabel>
      <Statement opacity={hold(frame, 16, 76)} lift={(1 - ease(frame, 16)) * 16}>
        Investigate first.
      </Statement>
      <Statement opacity={ease(frame, 84)} lift={(1 - ease(frame, 84)) * 16}>
        Diagnose only
        <br /><span style={{color: TEXT.amber}}>with evidence.</span>
      </Statement>
      <LowerThird opacity={ease(frame, 34)}>
        Potential shortfall is not confirmed recoverable energy. No cause has been
        established.
      </LowerThird>
    </>
  );
};

// --- Scene 7: product montage and close (38.0 - 42.0) ----------------------

const Close: React.FC = () => {
  const frame = useCurrentFrame();
  const pull = drive(frame, [0, 54], [1.06, 1.0]);
  const copy = ease(frame, 30, 16);

  return (
    <>
      <div style={{
        position: 'absolute', left: '50%', top: '36%', width: 1220, height: 780,
        transform: 'translate(-50%, -50%)', borderRadius: '50%',
        background: LIGHT.amberLit, opacity: 0.22, filter: 'blur(150px)',
      }} />
      <Camera shot={{zoom: pull, x: 0, y: -150, rotateY: -3, rotateX: 3}}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${TILE.columns}, ${CLOSE_TILE}px)`,
          gap: TILE.gap, transformStyle: 'preserve-3d',
        }}>
          {MONTAGE.map((item, i) => {
            const settle = drive(frame, [i * 2, 24 + i * 2], [0.55, 1]);
            return (
              <ScreenPanel key={item.label + i} frame={item.frame} width={CLOSE_TILE}
                radius={7} dim={i % 3 === 1 ? 0.16 : 0}
                style={{
                  transform: `translateZ(${(i % 3) * -16 - (1 - settle) * 110}px)`,
                  opacity: settle,
                }} />
            );
          })}
        </div>
      </Camera>
      <Scrim bottom={0.96} />

      <div style={{
        position: 'absolute', left: LAYOUT.safe, right: LAYOUT.safe, bottom: 74,
        fontFamily: FONT_STACK, opacity: copy,
        transform: `translateY(${(1 - copy) * 16}px)`,
      }}>
        <div style={{
          fontSize: 52, fontWeight: 700, lineHeight: 1.1, letterSpacing: -1.4,
          color: TEXT.bright, textShadow: '0 4px 28px rgba(0,0,0,0.78)',
        }}>
          Wind Underperformance
          <br />Decision Support
        </div>
        <div style={{height: 14}} />
        <div style={{fontSize: 29, fontWeight: 620, color: LIGHT.amberLit}}>
          Validate &#8594; Quantify &#8594; Challenge &#8594; Investigate
        </div>
        <div style={{height: 16}} />
        <div style={{fontSize: 22, lineHeight: 1.45, color: TEXT.muted}}>
          Independent portfolio case study &#183; Public ENGIE La Haute Borne
          data, Etalab Open Licence 2.0, via OpenOA
          <br />
          Not Clir Renewables software, data or methodology.
        </div>
      </div>
    </>
  );
};

// --- assembly --------------------------------------------------------------

export const WindDecisionFilmV2: React.FC = () => (
  <AbsoluteFill>
    <Environment>
      <Sequence from={SCENES.open.from} durationInFrames={SCENES.open.duration}>
        <Open />
      </Sequence>
      <Sequence from={SCENES.trust.from} durationInFrames={SCENES.trust.duration}>
        <DataTrust />
      </Sequence>
      <Sequence from={SCENES.scope.from} durationInFrames={SCENES.scope.duration}>
        <Scope />
      </Sequence>
      <Sequence from={SCENES.method.from} durationInFrames={SCENES.method.duration}>
        <Method />
      </Sequence>
      <Sequence from={SCENES.event.from} durationInFrames={SCENES.event.duration}>
        <Event />
      </Sequence>
      <Sequence from={SCENES.decide.from} durationInFrames={SCENES.decide.duration}>
        <Decide />
      </Sequence>
      <Sequence from={SCENES.close.from} durationInFrames={SCENES.close.duration}>
        <Close />
      </Sequence>
    </Environment>
  </AbsoluteFill>
);
