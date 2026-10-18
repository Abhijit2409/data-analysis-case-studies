import React from 'react';
import {
  Camera, Environment, LowerThird, Ring, ScreenLabel, ScreenPanel, Scrim,
  Spotlight, Statement, type Framing,
} from './components/Film';
import {MONTAGE, TILE} from './grid';
import {box, pad, union} from './screens';
import {FONT_STACK, LAYOUT, LIGHT, TEXT, TYPE} from './theme';

/**
 * Six style frames for the v2 product film.
 *
 * These are compositions, not mock-ups: they are rendered by the same code that
 * will render the film, from the same captures, so what is approved here is
 * what gets built. Each one is a held moment from a beat of the sequence.
 *
 * Every figure visible in any frame is part of a photograph of the running
 * application. The overlay copy carries no numbers of its own, which is the
 * rule that keeps the film honest: if a number is on screen, the product put
 * it there.
 */

// --- 1. Product cold open --------------------------------------------------

const COLD_OPEN: Framing = {screen: 'cockpit', x: 0, w: 1440, y: 0, h: 1454};

export const FrameColdOpen: React.FC = () => (
  <Environment>
    <Camera shot={{zoom: 1.0, x: 0, y: -74, rotateY: -5, rotateX: 2}}>
      <ScreenPanel frame={COLD_OPEN} width={1050}>
        <Ring box={pad(union(box('cockpit', 'gross'), box('cockpit', 'missing')), 16, 12)}
          opacity={0.9} />
      </ScreenPanel>
    </Camera>
    <Scrim />
    <ScreenLabel opacity={0.95}>Executive cockpit</ScreenLabel>
    <Statement opacity={1}>
      671.6 MWh of
      <br />apparent underperformance.
    </Statement>
    <LowerThird opacity={0.94}>
      Potential shortfall against a statistical reference &#8212; not confirmed
      recoverable energy.
    </LowerThird>
  </Environment>
);

// --- 2. Data trust ---------------------------------------------------------

const TIMESTAMP: Framing = {screen: 'datatrust', x: 906, w: 492, y: 706, h: 497};

export const FrameDataTrust: React.FC = () => (
  <Environment>
    <Camera shot={{zoom: 1.0, x: 0, y: -74, rotateY: 4, rotateX: 2}}>
      <ScreenPanel frame={TIMESTAMP} width={1050}>
        <Ring box={pad(box('datatrust', 'timestampChart'), 8, 6)} opacity={0.5} />
      </ScreenPanel>
    </Camera>
    <Scrim />
    <ScreenLabel opacity={0.95}>Data trust &#183; timestamp alignment</ScreenLabel>
    <Statement opacity={1}>
      The timestamps looked valid.
      <br />
      <span style={{color: TEXT.amber}}>They were not.</span>
    </Statement>
    <LowerThird opacity={0.94}>
      Corrected before any performance figure was computed.
    </LowerThird>
  </Environment>
);

// --- 3. Scope the exposure -------------------------------------------------

const ACCOUNTING: Framing = {screen: 'cockpit', y: 586, h: 1030};

export const FrameScope: React.FC = () => (
  <Environment>
    <Camera shot={{zoom: 1.0, x: 0, y: -74, rotateY: -4, rotateX: 2}}>
      <ScreenPanel frame={ACCOUNTING} width={1050}>
        <Spotlight box={pad(box('cockpit', 'missing'), 18, 14)} opacity={0.96} scrim={0.5} />
      </ScreenPanel>
    </Camera>
    <Scrim />
    <ScreenLabel opacity={0.95}>Executive cockpit &#183; 2015 energy accounting</ScreenLabel>
    <Statement opacity={1}>
      Missing is unknown
      <br />
      <span style={{color: TEXT.amber}}>&#8212; not zero.</span>
    </Statement>
    <LowerThird opacity={0.94}>
      2,074 ten-minute records hold no power or wind value. They cannot be
      quantified from this dataset.
    </LowerThird>
  </Environment>
);

// --- 4. Challenge the method -----------------------------------------------

const RANKING: Framing = {screen: 'cockpit', x: 850, w: 540, y: 790, h: 545};

export const FrameMethod: React.FC = () => (
  <Environment>
    <Camera shot={{zoom: 1.0, x: 0, y: -74, rotateY: 5, rotateX: 2}}>
      <ScreenPanel frame={RANKING} width={1050} />
    </Camera>
    <Scrim />
    <ScreenLabel opacity={0.95}>Executive cockpit &#183; shortfall per turbine</ScreenLabel>
    <Statement opacity={1}>
      Changing the reference
      <br />changed the priority.
    </Statement>
    <LowerThird opacity={0.94}>
      Prioritisation, not diagnosis. No cause is established by any method.
    </LowerThird>
  </Environment>
);

// --- 5. Investigation ------------------------------------------------------

const NEIGHBOURS: Framing = {screen: 'explorer', x: 370, w: 1004, y: 1838, h: 1014};

export const FrameInvestigation: React.FC = () => (
  <Environment>
    <Camera shot={{zoom: 1.0, x: 0, y: -74, rotateY: -4, rotateX: 2}}>
      <ScreenPanel frame={NEIGHBOURS} width={1050} />
    </Camera>
    <Scrim />
    <ScreenLabel opacity={0.95}>Investigation explorer &#183; neighbour comparison</ScreenLabel>
    <Statement opacity={1}>
      All three methods flag
      <br />the same interval.
    </Statement>
    <LowerThird opacity={0.94}>
      Neighbouring production confirms simultaneous peer operation; it does not
      identify the cause.
    </LowerThird>
  </Environment>
);

// --- 6. Product reveal -----------------------------------------------------

export const FrameReveal: React.FC = () => (
  <Environment>
    <div style={{
      position: 'absolute', left: '50%', top: '38%', width: 1180, height: 760,
      transform: 'translate(-50%, -50%)', borderRadius: '50%',
      background: LIGHT.amberLit, opacity: 0.2, filter: 'blur(150px)',
    }} />
    <Camera shot={{zoom: 1, x: 0, y: -186, rotateY: -3, rotateX: 3}}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${TILE.columns}, ${TILE.width}px)`,
        gap: TILE.gap, transformStyle: 'preserve-3d',
      }}>
        {MONTAGE.map((item, i) => (
          <ScreenPanel key={item.label + i} frame={item.frame} width={TILE.width}
            radius={7} dim={i % 3 === 1 ? 0.16 : 0}
            style={{transform: `translateZ(${(i % 3) * -16}px)`}} />
        ))}
      </div>
    </Camera>
    <Scrim />

    <div style={{
      position: 'absolute', left: LAYOUT.safe, right: LAYOUT.safe, bottom: 74,
      fontFamily: FONT_STACK,
    }}>
      <div style={{
        fontSize: 52, fontWeight: 700, lineHeight: 1.1,
        letterSpacing: -1.6, color: TEXT.bright,
        textShadow: '0 4px 28px rgba(0,0,0,0.75)',
      }}>
        Wind Underperformance
        <br />Decision Support
      </div>
      <div style={{height: 14}} />
      <div style={{
        fontSize: 27, fontWeight: 620, letterSpacing: 0.2, color: LIGHT.amberLit,
      }}>
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
  </Environment>
);

export const STYLE_FRAMES = [
  {id: 'V2Style1ColdOpen', component: FrameColdOpen},
  {id: 'V2Style2DataTrust', component: FrameDataTrust},
  {id: 'V2Style3Scope', component: FrameScope},
  {id: 'V2Style4Method', component: FrameMethod},
  {id: 'V2Style5Investigation', component: FrameInvestigation},
  {id: 'V2Style6Reveal', component: FrameReveal},
] as const;
