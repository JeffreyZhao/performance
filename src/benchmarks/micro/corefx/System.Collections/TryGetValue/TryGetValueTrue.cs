﻿// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Runtime.CompilerServices;
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Extensions;
using MicroBenchmarks;

namespace System.Collections
{
    [BenchmarkCategory(Categories.CoreFX, Categories.Collections, Categories.GenericCollections)]
    [GenericTypeArguments(typeof(int), typeof(int))] // value type
    [GenericTypeArguments(typeof(string), typeof(string))] // reference type
    [GenericTypeArguments(typeof(CustomValue), typeof(CustomValue))] // custom value type (more overhead)
    [GenericTypeArguments(typeof(CustomObject), typeof(CustomObject))] // custom reference type (less overhead)
    public class TryGetValueTrue<TKey, TValue>
    {
        private TKey[] _found;
        private Dictionary<TKey, TValue> _source;
        
        private HashSet<TKey> _hashSet;
        private Dictionary<TKey, TValue> _dictionary;
        private SortedList<TKey, TValue> _sortedList;
        private SortedDictionary<TKey, TValue> _sortedDictionary;
        private ConcurrentDictionary<TKey, TValue> _concurrentDictionary;
        private ImmutableDictionary<TKey, TValue> _immutableDictionary;
        private ImmutableSortedDictionary<TKey, TValue> _immutableSortedDictionary;

        [Params(Utils.DefaultCollectionSize)]
        public int Size;

        [GlobalSetup]
        public void Setup()
        {
            _found = ValuesGenerator.ArrayOfUniqueValues<TKey>(Size);
            _source = _found.ToDictionary(item => item, item => (TValue)(object)item);
            _hashSet = new HashSet<TKey>(_found);
            _dictionary = new Dictionary<TKey, TValue>(_source);
            _sortedList = new SortedList<TKey, TValue>(_source);
            _sortedDictionary = new SortedDictionary<TKey, TValue>(_source);
            _concurrentDictionary = new ConcurrentDictionary<TKey, TValue>(_source);
            _immutableDictionary = Immutable.ImmutableDictionary.CreateRange<TKey, TValue>(_source);
            _immutableSortedDictionary = Immutable.ImmutableSortedDictionary.CreateRange<TKey, TValue>(_source);
        }

        [Benchmark]
        public bool HashSet()
        {
            bool result = default;
            var collection = _hashSet;
            TKey[] found = _found;
            for (var i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool Dictionary()
        {
            bool result = default;
            Dictionary<TKey, TValue> collection = _dictionary;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        [BenchmarkCategory(Categories.CoreCLR, Categories.Virtual)]
        public bool IDictionary() => TryGetValue(_dictionary);
        
        [MethodImpl(MethodImplOptions.NoInlining)]
        private bool TryGetValue(IDictionary<TKey, TValue> collection)
        {
            bool result = default;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool SortedList()
        {
            bool result = default;
            SortedList<TKey, TValue> collection = _sortedList;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool SortedDictionary()
        {
            bool result = default;
            SortedDictionary<TKey, TValue> collection = _sortedDictionary;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool ConcurrentDictionary()
        {
            bool result = default;
            ConcurrentDictionary<TKey, TValue> collection = _concurrentDictionary;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool ImmutableDictionary()
        {
            bool result = default;
            ImmutableDictionary<TKey, TValue> collection = _immutableDictionary;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }

        [Benchmark]
        public bool ImmutableSortedDictionary()
        {
            bool result = default;
            ImmutableSortedDictionary<TKey, TValue> collection = _immutableSortedDictionary;
            TKey[] found = _found;
            for (int i = 0; i < found.Length; i++)
                result ^= collection.TryGetValue(found[i], out _);
            return result;
        }
    }
}