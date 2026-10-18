import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// Portrait 1080x1350 for the LinkedIn feed; dimensions are set on the
// Composition itself so stills and renders cannot drift apart.
