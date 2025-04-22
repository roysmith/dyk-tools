"use strict";

const dedent = require('dedent');

const { describe } = require('node:test');

const { HookSet } = require('./hookset');
const { Hook } = require('./hook');
const { Link } = require('./link');

describe('constructor', () => {
    it('constructs a default instance', () => {
        const hs = new HookSet('My Title', 'foo', []);
        expect(hs).toBeInstanceOf(HookSet);
        expect(hs.title).toEqual('My Title');
        expect(hs.wikitext).toBe('foo');
        expect(hs.hooks).toEqual([]);
    });
});

describe('loadWikitext', () => {
    it('calls api.get()', async () => {
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                "parse": {
                    "title": "Template:Did you know/Queue/1",
                    "pageid": 19951383,
                    "wikitext": "{{DYKbotdo|xxx}}"
                }
            });

        const wikitext = HookSet.loadWikitext('My Queue');

        expect(mw.Api.prototype.get).toHaveBeenCalledTimes(1);
        expect(mw.Api.prototype.get).toHaveBeenCalledWith({
            action: 'parse',
            format: 'json',
            page: "My Queue",
            prop: 'wikitext',
            formatversion: 2,
        });
        await expect(wikitext).resolves.toBe('{{DYKbotdo|xxx}}');
    });
});

describe('findHooks', () => {
    it('parses the hooks', () => {
        const wikitext = dedent(
            `<!--Hooks-->
            {{main page image/DYK}}
            * ... that '''[[foo]]''' blah?
            * ... that '''[[foo|bar]]''' and '''[[baz]]'''{{-?}}
            <!--HooksEnd-->`);

        const hooks = Array.from(HookSet.findHooks(wikitext));

        expect(hooks).toEqual([
            new Hook("* ... that '''[[foo]]''' blah?", [
                new Link('foo', ''),
            ]),
            new Hook("* ... that '''[[foo|bar]]''' and '''[[baz]]'''{{-?}}", [
                new Link('foo', 'bar'),
                new Link('baz', ''),
            ]),
        ]);
    });
});


