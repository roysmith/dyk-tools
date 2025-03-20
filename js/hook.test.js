"use strict";

const { describe } = require('node:test');

const { Hook, Link } = require('./hook');

describe('Link constructor', () => {
    it('creates an plain link', () => {
        const link = new Link('foo');
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('');
    });
});

describe('Link constructor', () => {
    it('creates an piped link', () => {
        const link = new Link('foo|bar');
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('bar');
    });
});

describe('Link constructor', () => {
    it('strips brackets', () => {
        const link = new Link('[[foo]]');
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('');
    });
});

describe('Hook constructor', () => {
    it('finds bolded links', () => {
        const hook = new Hook("... that '''[[Foo|bar]]''' is [[Not me]]?");
        expect(hook).toBeInstanceOf(Hook);
        expect(hook.text).toEqual("... that '''[[Foo|bar]]''' is [[Not me]]?");
        expect(hook.links).toEqual(
            [new Link('[[Foo|bar]]')],
        );
    });
});

describe('Hook constructor', () => {
    it('finds multiple bolded links', () => {
        const hook = new Hook("... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?");
        expect(hook).toBeInstanceOf(Hook);
        expect(hook.links).toEqual([
            new Link('[[Sound Transit]]'),
            new Link('[[permanent public art]]'),
        ]);
    });
});
