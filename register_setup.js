// For issues with command deprecation, we need to use a loader instead.
// https://github.com/nodejs/node/issues/51196#issuecomment-1998216742
import { register } from 'node:module';
import { pathToFileURL } from 'node:url';
register('ts-node/esm', pathToFileURL('./'));
