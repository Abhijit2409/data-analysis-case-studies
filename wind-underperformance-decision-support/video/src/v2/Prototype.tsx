import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {
  Camera, Cursor, Environment, LowerThird, Ring, ScreenLabel, ScreenPanel, Scrim,
  Statement, between, centre, drive, focusOn, type Framing, type Shot,
} from './components/Film';
import {MONTAGE, TILE} from './grid';
import {box, clicked, pad, union} from './screens';
import {FONT_STACK, LAYOUT, LIGHT, TEXT} from './theme';

/**
 * v2 motion prototype - 11.6 seconds, for approving the art direction.
 *
 * It contains one of each thing the full film depends on:
 *   1. a dark product cold open with the panel arriving in depth
 *   2. a cursor interaction on a control that genuinely exists
 *   3. a continuous camera move from one application page to another, with
 *      both on screen while the camera travels
 *   4. the push-in to the R80711 neighbour chart
 *   5. a pull-back to the twelve-tile product montage
 *
 * The rule underneath all of it: every figure on screen is part of a photograph
 * of the running application. Overlay copy carries no figures of its own except
 * the cold-open number, which the application renders in the same frame.
 */

const FULL: Framing = {screen: 'cockpit', x: 0, w: 1440, y: 0, h: 1454};
const FULL_GROSS: Framing = {screen: 'cockpit_gross', x: 0, w: 1440, y: 0, h: 1454};
const NEIGHBOURS: Framing = {screen: 'explorer', x: 370, w: 1004, y: 1838, h: 1014};

const PANEL_W = 1050;
const ROOM_GAP = 260;

/** Half the distance between the two panel centres when they sit side by side. */
const ROOM_SHIFT = (ROOM_GAP + PANEL_W) / 2;

/** Cut points, in frames. Cuts land mid-move, never at rest. */
export const BEATS = {
  open: {from: 0, duration: 96},
  interact: {from: 96, duration: 96},
  travel: {from: 192, duration: 96},
  reveal: {from: 288, duration: 60},
} as const;

export const PROTOTYPE_FRAMES = 348; // 11.6s at 30fps

/** The shot the cold open ends on and the interaction begins from. */
const ACCOUNTING_SHOT = focusOn({
  at: centre(union(box('cockpit', 'gross'), box('cockpit', 'missing'))),
  crop: FULL, width: PANEL_W, zoom: 1.24, rotateY: -5, rotateX: 2,
});

/** The whole cockpit page, centred. The interaction ends here and the travel
 *  begins here, so the cut between them is seamless. */
const PAGE_SHOT: Shot = {zoom: 1.08, x: 0, y: 0, rotateY: 2, rotateX: 1};

// --- 1. Product cold open --------------------------------------------------

const ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const arrive = drive(frame, [0, 40], [0.28, 1]);
  const settle = drive(frame, [8, 96], [0, 1]);

  const shot: Shot = {
    zoom: drive(frame, [8, 96], [0.96, ACCOUNTING_SHOT.zoom]),
    rotateY: drive(frame, [0, 96], [-13, -5]),
    rotateX: 2,
    x: ACCOUNTING_SHOT.x * settle,
    y: ACCOUNTING_SHOT.y * settle - 70 * (1 - settle),
  };

  const ring = interpolate(frame, [54, 70], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const copy = interpolate(frame, [22, 36], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <>
      <Camera shot={shot}>
        <div style={{opacity: arrive, transform: `translateZ(${(1 - arrive) * -300}px)`}}>
          <ScreenPanel frame={FULL} width={PANEL_W}>
            <Ring box={pad(union(box('cockpit', 'gross'), box('cockpit', 'missing')), 16, 12)}
              opacity={ring} />
          </ScreenPanel>
        </div>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={copy}>Executive cockpit</ScreenLabel>
      <Statement opacity={copy} lift={(1 - copy) * 16}>
        671.6 MWh of
        <br />apparent underperformance.
      </Statement>
      <LowerThird opacity={interpolate(frame, [40, 54], [0, 1],
        {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}>
        Potential shortfall against a statistical reference &#8212; not confirmed
        recoverable energy.
      </LowerThird>
    </>
  );
};

// --- 2. A real control, really clicked -------------------------------------

/**
 * The cursor travels to the Energy basis radio and clicks "Gross residual
 * shortfall". That control exists in app/app.py, and switching it genuinely
 * changes the page - so the panel swaps to the capture taken after the real
 * click. The camera then pulls back to the whole page, where the next beat
 * starts from.
 */
const CLICK_AT = 46;

const Interact: React.FC = () => {
  const frame = useCurrentFrame();
  const target = clicked('cockpit_gross');

  const controlShot = focusOn({
    at: {x: 900, y: 500},
    crop: FULL, width: PANEL_W, zoom: 1.46, rotateY: 4, rotateX: 2,
  });
  const shot = frame < 56
    ? between(frame, [0, 42], ACCOUNTING_SHOT, controlShot)
    : between(frame, [56, 96], controlShot, PAGE_SHOT);

  const travel = drive(frame, [8, CLICK_AT - 4], [0, 1]);
  const from = {x: 980, y: 470};
  const to = {x: target.x - 14, y: target.y + 6};
  const press = interpolate(frame, [CLICK_AT, CLICK_AT + 14], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const copy = interpolate(frame, [16, 30], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <>
      <Camera shot={shot}>
        <ScreenPanel frame={frame >= CLICK_AT ? FULL_GROSS : FULL} width={PANEL_W}>
          <Ring box={pad(target, 14, 10)}
            opacity={interpolate(frame, [20, 32], [0, 0.85],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
          <Cursor
            x={from.x + (to.x - from.x) * travel}
            y={from.y + (to.y - from.y) * travel}
            opacity={interpolate(frame, [62, 76], [1, 0],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
            press={press < 1 ? press : 0}
          />
        </ScreenPanel>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={copy}>Executive cockpit &#183; energy basis</ScreenLabel>
      <Statement opacity={copy} lift={(1 - copy) * 16}>
        The basis is a choice,
        <br />
        <span style={{color: TEXT.amber}}>not a given.</span>
      </Statement>
      <LowerThird opacity={interpolate(frame, [52, 66], [0, 1],
        {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}>
        Gross residual shortfall includes short dips that fail the one-hour
        persistence rule.
      </LowerThird>
    </>
  );
};

// --- 3. Travel to the next screen, then push in ----------------------------

/**
 * Both pages sit in the same room, side by side. The camera dollies from one to
 * the other with both on screen while it travels, then pushes into the
 * neighbour chart. This is a panel-to-panel move rather than a cut.
 */
const Travel: React.FC = () => {
  const frame = useCurrentFrame();

  // Centring the left panel pushes the row right; centring the right panel
  // pulls it left by the same distance.
  const atCockpit: Shot = {...PAGE_SHOT, x: ROOM_SHIFT * PAGE_SHOT.zoom};
  const atExplorer: Shot = {zoom: 1.0, x: -ROOM_SHIFT, y: 0, rotateY: -4, rotateX: 1};
  const pushed: Shot = {zoom: 1.2, x: -ROOM_SHIFT * 1.2, y: -40, rotateY: -2, rotateX: 1};

  const shot = frame < 44
    ? between(frame, [0, 44], atCockpit, atExplorer)
    : between(frame, [44, 96], atExplorer, pushed);

  const copy = interpolate(frame, [46, 60], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const label = interpolate(frame, [30, 44], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <>
      <Camera shot={shot}>
        <div style={{display: 'flex', alignItems: 'center', gap: ROOM_GAP}}>
          {/* The page we are leaving dims as the camera passes it. */}
          <ScreenPanel frame={FULL_GROSS} width={PANEL_W}
            dim={drive(frame, [0, 44], [0, 0.45])} />
          <ScreenPanel frame={NEIGHBOURS} width={PANEL_W} />
        </div>
      </Camera>
      <Scrim />
      <ScreenLabel opacity={label}>
        Investigation explorer &#183; neighbour comparison
      </ScreenLabel>
      <Statement opacity={copy} lift={(1 - copy) * 16}>
        All three methods flag
        <br />the same interval.
      </Statement>
      <LowerThird opacity={interpolate(frame, [64, 78], [0, 1],
        {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}>
        Neighbouring production confirms simultaneous peer operation; it does not
        identify the cause.
      </LowerThird>
    </>
  );
};

// --- 4. Pull back to the product -------------------------------------------

const Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  const pull = drive(frame, [0, 44], [1.34, 1.0]);
  const copy = interpolate(frame, [24, 40], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <>
      <div style={{
        position: 'absolute', left: '50%', top: '38%', width: 1180, height: 760,
        transform: 'translate(-50%, -50%)', borderRadius: '50%',
        background: LIGHT.amberLit, opacity: 0.2, filter: 'blur(150px)',
      }} />
      <Camera shot={{zoom: pull, x: 0, y: -186, rotateY: -3, rotateX: 3}}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${TILE.columns}, ${TILE.width}px)`,
          gap: TILE.gap, transformStyle: 'preserve-3d',
        }}>
          {MONTAGE.map((item, i) => {
            // The wall assembles row by row as the camera retreats.
            const settle = drive(frame, [i * 2, 22 + i * 2], [0.55, 1]);
            return (
              <ScreenPanel key={item.label + i} frame={item.frame} width={TILE.width}
                radius={7} dim={i % 3 === 1 ? 0.16 : 0}
                style={{
                  transform: `translateZ(${(i % 3) * -16 - (1 - settle) * 90}px)`,
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
          color: TEXT.bright, textShadow: '0 4px 28px rgba(0,0,0,0.75)',
        }}>
          Wind Underperformance
          <br />Decision Support
        </div>
        <div style={{height: 14}} />
        <div style={{fontSize: 27, fontWeight: 620, color: LIGHT.amberLit}}>
          Validate &#8594; Quantify &#8594; Challenge &#8594; Investigate
        </div>
        <div style={{height: 16}} />
        <div style={{fontSize: 19, lineHeight: 1.5, color: TEXT.muted}}>
          Independent portfolio case study &#8212; not Clir Renewables software,
          data or methodology.
          <br />
          Public data: ENGIE La Haute Borne, Etalab Open Licence 2.0, via OpenOA.
        </div>
      </div>
    </>
  );
};

// --- assembly --------------------------------------------------------------

export const V2Prototype: React.FC = () => (
  <AbsoluteFill>
    <Environment>
      <Sequence from={BEATS.open.from} durationInFrames={BEATS.open.duration}>
        <ColdOpen />
      </Sequence>
      <Sequence from={BEATS.interact.from} durationInFrames={BEATS.interact.duration}>
        <Interact />
      </Sequence>
      <Sequence from={BEATS.travel.from} durationInFrames={BEATS.travel.duration}>
        <Travel />
      </Sequence>
      <Sequence from={BEATS.reveal.from} durationInFrames={BEATS.reveal.duration}>
        <Reveal />
      </Sequence>
    </Environment>
  </AbsoluteFill>
);
