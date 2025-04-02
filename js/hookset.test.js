"use strict";

const dedent = require('dedent');

const { describe } = require('node:test');

const { HookSet } = require('./hookset');
const { Hook } = require('./hook');
const { Link } = require('./link');

describe('constructor', async () => {
    it('constructs a default instance', async () => {
        const hs = new HookSet('My Title', 'foo', []);
        expect(hs).toBeInstanceOf(HookSet);
        expect(hs.title).toEqual('My Title');
        expect(hs.wikitext).toBe('foo');
        expect(hs.hooks).toEqual([]);
    });
});

describe('load', () => {
    it('calls api.get()', async () => {
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                "parse": {
                    "title": "Template:Did you know/Queue/1",
                    "pageid": 19951383,
                    "wikitext": "{{DYKbotdo|xxx}}"
                }
            });

        const wikitext = HookSet.load('My Queue');

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

describe('findHookLines', () => {
    it('parses the hooks', async () => {
        const wikitext = dedent(
            `Blah blah
            <!--Hooks-->
            {{main page image}}
            * ... that politician '''[[Prasenjit Barman]]''' was credited for leading the restoration of the [[Cooch Behar Palace]]?
            * ... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?
            <!--HooksEnd-->
            {{ flatlist| class=dyk - footer noprint | style=margin - top: 0.5em; text - align: right;}}
             `
        );

        const lines = HookSet.findHookLines(wikitext);

        expect(lines).toEqual([
            "* ... that politician '''[[Prasenjit Barman]]''' was credited for leading the restoration of the [[Cooch Behar Palace]]?",
            "* ... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?",
        ]);
    });
});

describe('findHooks', () => {
    it('parses the hooks', async () => {
        const wikitext = dedent(
            `<!--Hooks-->
            * ... that '''[[foo]]''' blah?
            * ... that '''[[foo|bar]]''' and '''[[baz]]'''{{-?}}
            <!--HooksEnd-->`);

        const hooks = HookSet.findHooks(wikitext);

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


