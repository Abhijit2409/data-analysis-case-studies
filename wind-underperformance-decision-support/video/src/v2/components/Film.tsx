import React from 'react';
import {Img, interpolate, useCurrentFrame} from 'remotion';
import {CAPTURE_WIDTH, CONTENT, type Box, type ScreenName, screen} from '../screens';
import {FONT_STACK, LAYOUT, LIGHT, ROOM, TEXT, TYPE} from '../theme';

/**
 * The building blocks of the v2 product film.
 *
 * The idea running through all of them: the application is a real object in a
 * dark room. The Environment is the room, ScreenPanel is the object, Camera
 * moves the viewer, and Spotlight and Cursor are how attention is directed at
 * one part of a real interface without altering it.
 */

// --- easing ----------------------------------------------------------------

/** Slow in, slow out. Camera moves use this so nothing starts or stops abruptly. */
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

/** Eased interpolation between two values over a frame range. */
export const drive = (
  frame: number, range: [number, number], values: [number, number],
) => {
  const t = interpolate(frame, range, [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return values[0] + (values[1] - values[0]) * ease(t);
};

// --- the room --------------------------------------------------------------

/**
 * The dark environment. Three soft lights - blue high left, teal low left,
 * amber right - give the panels something to catch, and a vignette keeps the
 * eye in the middle of the frame.
 */
export const Environment: React.FC<{children: React.ReactNode; drift?: number}> = ({
  children, drift = 0,
}) => (
  <div
    style={{
      position: 'absolute', inset: 0, overflow: 'hidden',
      background: `radial-gradient(130% 90% at 50% 18%, ${ROOM.rise} 0%, ${ROOM.base} 52%, ${ROOM.deep} 100%)`,
      fontFamily: FONT_STACK,
    }}
  >
    <div style={{
      position: 'absolute', left: -340 + drift * 0.5, top: -260,
      width: 1100, height: 900, borderRadius: '50%',
      background: LIGHT.blue, opacity: 0.2, filter: 'blur(190px)',
    }} />
    <div style={{
      position: 'absolute', right: -420 - drift * 0.7, top: 420,
      width: 1000, height: 1000, borderRadius: '50%',
      background: LIGHT.amber, opacity: 0.16, filter: 'blur(210px)',
    }} />
    <div style={{
      position: 'absolute', left: -260, bottom: -340,
      width: 900, height: 800, borderRadius: '50%',
      background: LIGHT.teal, opacity: 0.13, filter: 'blur(200px)',
    }} />
    {children}
    <div style={{
      position: 'absolute', inset: 0, pointerEvents: 'none',
      background: 'radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.55) 100%)',
    }} />
  </div>
);

// --- the camera ------------------------------------------------------------

export type Shot = {
  /** Scale about the frame centre. 1 = the panel at its natural placement. */
  zoom: number;
  /** Translation in frame pixels. */
  x: number;
  y: number;
  /** Degrees. Small values only - this is a restrained camera. */
  rotateY?: number;
  rotateX?: number;
};

/** Moves the viewer rather than the object, so panels keep their own geometry. */
export const Camera: React.FC<{shot: Shot; children: React.ReactNode}> = ({
  shot, children,
}) => (
  <div style={{
    position: 'absolute', inset: 0,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    perspective: 2400, perspectiveOrigin: '50% 45%',
  }}>
    <div style={{
      transformStyle: 'preserve-3d',
      transform: `translate3d(${shot.x}px, ${shot.y}px, 0) scale(${shot.zoom}) `
        + `rotateY(${shot.rotateY ?? 0}deg) rotateX(${shot.rotateX ?? 0}deg)`,
    }}>
      {children}
    </div>
  </div>
);

/** Eases between two camera positions. */
export const between = (
  frame: number, range: [number, number], from: Shot, to: Shot,
): Shot => ({
  zoom: drive(frame, range, [from.zoom, to.zoom]),
  x: drive(frame, range, [from.x, to.x]),
  y: drive(frame, range, [from.y, to.y]),
  rotateY: drive(frame, range, [from.rotateY ?? 0, to.rotateY ?? 0]),
  rotateX: drive(frame, range, [from.rotateX ?? 0, to.rotateX ?? 0]),
});

// --- the application panel -------------------------------------------------

export type Framing = {
  screen: ScreenName;
  /** Crop rectangle in the capture's own CSS pixels. */
  x?: number; y: number; w?: number; h: number;
};

/**
 * A floating slab showing a crop of a real application capture.
 *
 * Children are positioned in the CAPTURE's coordinate space, the same space
 * boxes.json reports, so a spotlight or cursor written as {x: 881, y: 807}
 * lands on the element the browser measured at those coordinates.
 */
export const ScreenPanel: React.FC<{
  frame: Framing;
  /** On-screen width of the panel in frame pixels. */
  width: number;
  children?: React.ReactNode;
  radius?: number;
  dim?: number;
  style?: React.CSSProperties;
}> = ({frame: f, width, children, radius = 18, dim = 0, style}) => {
  const cropX = f.x ?? CONTENT.x;
  const cropW = f.w ?? CONTENT.w;
  const scale = width / cropW;
  const height = f.h * scale;
  const {src} = screen(f.screen);

  return (
    <div style={{
      position: 'relative', width, height, borderRadius: radius,
      // Depth: a long soft shadow for the drop, a tight one for contact, and a
      // lit top edge so the slab reads as a physical object under the key light.
      boxShadow: '0 70px 150px rgba(0,0,0,0.62), 0 18px 46px rgba(0,0,0,0.48), '
        + `inset 0 1px 0 ${ROOM.panelEdgeLit}, 0 0 0 1px ${ROOM.panelEdge}`,
      overflow: 'hidden', clipPath: `inset(0 round ${radius}px)`,
      transformStyle: 'flat', background: '#ffffff', flexShrink: 0, ...style,
    }}>
      <div style={{
        position: 'absolute', top: 0, left: 0, transformOrigin: '0 0',
        transform: `scale(${scale}) translate(${-cropX}px, ${-f.y}px)`,
      }}>
        <Img src={src} style={{width: CAPTURE_WIDTH, display: 'block'}} alt="" />
        {children}
      </div>
      {dim > 0 ? (
        <div style={{
          position: 'absolute', inset: 0, background: ROOM.base, opacity: dim,
        }} />
      ) : null}
    </div>
  );
};

// --- directing attention ---------------------------------------------------

/**
 * Darkens the whole panel except one measured element.
 *
 * Drawn as a huge spread shadow around the box, so the interface underneath is
 * never covered or redrawn - only dimmed.
 */
export const Spotlight: React.FC<{
  box: Box; opacity: number; radius?: number; ring?: string; scrim?: number;
}> = ({box: b, opacity, radius = 10, ring = LIGHT.amberLit, scrim = 0.52}) => (
  <div style={{
    position: 'absolute', left: b.x, top: b.y, width: b.w, height: b.h,
    borderRadius: radius, opacity,
    boxShadow: `0 0 0 9999px rgba(7, 9, 13, ${scrim})`,
    outline: `2px solid ${ring}`, outlineOffset: 3,
  }} />
);

/** A plain focus ring, for when dimming the rest would hide needed context. */
export const Ring: React.FC<{box: Box; opacity: number; colour?: string}> = ({
  box: b, opacity, colour = LIGHT.amberLit,
}) => (
  <div style={{
    position: 'absolute', left: b.x - 6, top: b.y - 6,
    width: b.w + 12, height: b.h + 12, borderRadius: 10,
    border: `2px solid ${colour}`, opacity,
    boxShadow: `0 0 26px ${colour}55`,
  }} />
);

/**
 * The pointer. Positioned in capture coordinates, so it scales with the panel
 * exactly as a cursor does in a screen recording the viewer zooms into.
 */
export const Cursor: React.FC<{x: number; y: number; opacity?: number; press?: number}> = ({
  x, y, opacity = 1, press = 0,
}) => (
  <div style={{position: 'absolute', left: x, top: y, opacity}}>
    {press > 0 ? (
      <div style={{
        position: 'absolute', left: -26, top: -26, width: 52, height: 52,
        borderRadius: '50%', border: `2px solid ${LIGHT.amberLit}`,
        transform: `scale(${0.3 + press * 1.1})`, opacity: 1 - press,
      }} />
    ) : null}
    <svg width={30} height={38} viewBox="0 0 30 38" style={{
      display: 'block', filter: 'drop-shadow(0 3px 6px rgba(0,0,0,0.5))',
      transform: `scale(${1 - press * 0.12})`, transformOrigin: '2px 2px',
    }}>
      <path d="M2 2 L2 27 L8.6 20.8 L12.8 30.5 L17.1 28.6 L13 19.2 L22 18.8 Z"
        fill="#ffffff" stroke="#11161d" strokeWidth={1.6} strokeLinejoin="round" />
    </svg>
  </div>
);

// --- overlay copy ----------------------------------------------------------

/**
 * One short statement at a time. Never a full screen of text: it sits over the
 * product, in the lower part of the frame, and the product keeps moving behind.
 */
export const Statement: React.FC<{
  children: React.ReactNode; opacity: number; lift?: number;
  tone?: string; size?: number; align?: 'left' | 'center';
}> = ({children, opacity, lift = 0, tone = TEXT.bright, size = TYPE.statement, align = 'left'}) => (
  <div style={{
    position: 'absolute', left: LAYOUT.safe, right: LAYOUT.safe, bottom: 240,
    opacity, transform: `translateY(${lift}px)`, textAlign: align,
  }}>
    <div style={{
      fontFamily: FONT_STACK, fontSize: size, fontWeight: 650, lineHeight: 1.14,
      letterSpacing: -1.2, color: tone,
      textShadow: '0 4px 28px rgba(0,0,0,0.72), 0 1px 3px rgba(0,0,0,0.6)',
    }}>
      {children}
    </div>
  </div>
);

/** The qualification line. Small, factual, and never the headline. */
export const LowerThird: React.FC<{children: React.ReactNode; opacity: number}> = ({
  children, opacity,
}) => (
  <div style={{
    position: 'absolute', left: LAYOUT.safe, right: LAYOUT.safe, bottom: 86,
    opacity, fontFamily: FONT_STACK, fontSize: TYPE.lower, lineHeight: 1.4,
    color: TEXT.body, borderLeft: `3px solid ${LIGHT.amberLit}`, paddingLeft: 18,
    textShadow: '0 2px 16px rgba(0,0,0,0.75)',
  }}>
    {children}
  </div>
);

/** The page label, so the viewer always knows which screen they are looking at. */
export const ScreenLabel: React.FC<{children: React.ReactNode; opacity: number}> = ({
  children, opacity,
}) => (
  <div style={{
    position: 'absolute', left: LAYOUT.safe, top: 46, opacity,
    fontFamily: FONT_STACK, fontSize: TYPE.micro, fontWeight: 620,
    letterSpacing: 2.4, textTransform: 'uppercase', color: TEXT.muted,
    textShadow: '0 2px 14px rgba(0,0,0,0.8)',
  }}>
    {children}
  </div>
);

/** Convenience: a fade that can also lift, for overlay copy. */
export const useFade = (at: number, length = 12) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [at, at + length], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return {opacity: t, lift: (1 - t) * 14};
};

// --- aiming the camera -----------------------------------------------------

/**
 * Builds the camera position that puts a point of the CAPTURE at the centre of
 * the frame at a given zoom.
 *
 * Camera moves are written as "look at the Energy basis control" rather than as
 * pixel offsets, so a move still lands correctly if a panel is resized.
 */
export const focusOn = (opts: {
  /** The point to centre, in capture CSS coordinates. */
  at: {x: number; y: number};
  /** The panel's framing and on-screen width, as given to ScreenPanel. */
  crop: {x?: number; y: number; w?: number; h: number};
  width: number;
  zoom: number;
  rotateY?: number;
  rotateX?: number;
}): Shot => {
  const cropX = opts.crop.x ?? CONTENT.x;
  const cropW = opts.crop.w ?? CONTENT.w;
  const scale = opts.width / cropW;
  const panelHeight = opts.crop.h * scale;
  // Where the point sits inside the panel, measured from the panel's centre.
  const px = (opts.at.x - cropX) * scale - opts.width / 2;
  const py = (opts.at.y - opts.crop.y) * scale - panelHeight / 2;
  return {
    zoom: opts.zoom,
    x: -px * opts.zoom,
    y: -py * opts.zoom,
    rotateY: opts.rotateY ?? 0,
    rotateX: opts.rotateX ?? 0,
  };
};

/** The centre of a measured element, for use with focusOn. */
export const centre = (b: Box) => ({x: b.x + b.w / 2, y: b.y + b.h / 2});


/**
 * Darkens the top and bottom of the frame so overlay copy stays readable over a
 * bright application panel. Placed between the camera and the copy, never over
 * the middle of the frame, so the product itself is never muddied.
 */
export const Scrim: React.FC<{top?: number; bottom?: number}> = ({
  top = 0.9, bottom = 0.96,
}) => (
  <>
    <div style={{
      position: 'absolute', left: 0, right: 0, top: 0, height: 210,
      pointerEvents: 'none',
      background: `linear-gradient(to bottom, rgba(7,9,13,${top}) 0%, `
        + `rgba(7,9,13,${top * 0.5}) 46%, rgba(7,9,13,0) 100%)`,
    }} />
    <div style={{
      position: 'absolute', left: 0, right: 0, bottom: 0, height: 580,
      pointerEvents: 'none',
      background: `linear-gradient(to top, rgba(7,9,13,${bottom}) 0%, `
        + `rgba(7,9,13,${bottom * 0.92}) 34%, rgba(7,9,13,0) 100%)`,
    }} />
  </>
);

// --- callouts --------------------------------------------------------------

/**
 * A chip that names a measured element, joined to it by a short leader line.
 *
 * It lives in the capture's coordinate space, so it tracks the interface as the
 * camera moves. `size` is given in capture pixels: divide the on-screen size you
 * want by the panel scale times the camera zoom.
 *
 * A callout may only restate what the element already shows. It is a pointer,
 * not a new claim.
 */
export const Callout: React.FC<{
  box: Box;
  children: React.ReactNode;
  opacity: number;
  /** Which side of the element the chip sits on. */
  side?: 'above' | 'below';
  size?: number;
  tone?: string;
  offset?: number;
}> = ({box: b, children, opacity, side = 'above', size = 30, tone = LIGHT.amberLit, offset = 34}) => {
  const lineHeight = offset;
  const chipBottom = side === 'above';
  return (
    <div style={{
      position: 'absolute',
      left: b.x + b.w / 2,
      top: chipBottom ? b.y - lineHeight : b.y + b.h + lineHeight,
      opacity,
      transform: 'translateX(-50%)',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
    }}>
      {!chipBottom ? (
        <div style={{width: 2, height: lineHeight, background: tone, opacity: 0.85}} />
      ) : null}
      <div style={{
        whiteSpace: 'nowrap',
        fontFamily: FONT_STACK, fontSize: size, fontWeight: 680,
        letterSpacing: -0.2, color: '#0b0e13',
        background: tone, borderRadius: size * 0.28,
        padding: `${size * 0.3}px ${size * 0.62}px`,
        boxShadow: '0 10px 30px rgba(0,0,0,0.45)',
      }}>
        {children}
      </div>
      {chipBottom ? (
        <div style={{width: 2, height: lineHeight, background: tone, opacity: 0.85}} />
      ) : null}
    </div>
  );
};

/** A row of small figures, used where several numbers describe one event. */
export const StatStrip: React.FC<{
  items: {value: string; label: string}[];
  opacity: number;
  lift?: number;
}> = ({items, opacity, lift = 0}) => (
  <div style={{
    position: 'absolute', left: LAYOUT.safe - 18, right: LAYOUT.safe - 18, bottom: 436,
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px 26px',
    opacity, transform: `translateY(${lift}px)`,
    fontFamily: FONT_STACK, padding: '18px 20px 16px',
    background: 'rgba(8, 11, 16, 0.84)', borderRadius: 12,
    border: '1px solid rgba(255,255,255,0.09)',
    backdropFilter: 'blur(6px)',
  }}>
    {items.map((item) => (
      <div key={item.label}>
        <div style={{
          fontSize: 50, fontWeight: 720, color: TEXT.bright, letterSpacing: -1,
          textShadow: '0 3px 20px rgba(0,0,0,0.85)',
        }}>
          {item.value}
        </div>
        <div style={{
          fontSize: 27, fontWeight: 560, color: TEXT.body, lineHeight: 1.2,
          marginTop: 4, textShadow: '0 2px 14px rgba(0,0,0,0.9)',
        }}>
          {item.label}
        </div>
      </div>
    ))}
  </div>
);
