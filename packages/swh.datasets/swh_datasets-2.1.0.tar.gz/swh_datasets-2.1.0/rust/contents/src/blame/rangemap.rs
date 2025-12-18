// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::cmp::{min, Ordering};
use std::iter::Peekable;
use std::ops::Range;

/// Stores annotations on a sequence of elements indexed from 0 to N.
/// Each annotation is defined by a interval of indices and an annotating
/// value of type `T`.
///
/// It would generally be more efficient to implement such a structure using
/// linked lists. A range can be split and refined into smaller ranges
/// (when we discover a commit that changes parts of it), while keeping the
/// rest of the list intact.
/// Unfortunately, linked lists don't fit well in Rust's ownership model, making
/// it very hard to reach the desired complexity improvement without doing a lot
/// of unsafe things.
/// Therefore, the designated way to make a change to a [`RangeMap`] is to [`RangeMap::zip`]
/// it with another one (or use the standalone method [`zip_range_iterators`]), map
/// the iterator to a `(Range<usize>, T)` pair and `.collect()` it to obtain the
/// new version of the [`RangeMap`].
#[derive(Debug)]
pub struct RangeMap<T> {
    ranges: Vec<(Range<usize>, T)>,
}

impl<T> RangeMap<T> {
    /// Create a new range map from a sorted list of
    /// `(range_start, value)` pairs.
    pub fn new<I>(ranges: I) -> Self
    where
        I: IntoIterator<Item = (Range<usize>, T)>,
    {
        let mut max_seen = 0;
        let ranges = ranges.into_iter().filter(move |(range, _)| {
            if range.start < max_seen {
                panic!("Cannot create a RangeMap out of unsorted ranges");
            }
            max_seen = range.end;
            range.start != range.end
        });
        RangeMap {
            ranges: ranges.collect(),
        }
    }

    /// Gets the range containing the requested index
    /// and its associated value. It has logarithmic
    /// complexity in the number of ranges stored.
    pub fn get(&self, index: usize) -> Option<&(Range<usize>, T)> {
        let binary_search_result = self
            .ranges
            .binary_search_by(|(range, _)| {
                if index < range.start {
                    Ordering::Greater
                } else if index >= range.start && index < range.end {
                    Ordering::Equal
                } else {
                    Ordering::Less
                }
            })
            .ok()?;
        Some(&self.ranges[binary_search_result])
    }

    /// Compute the list of ranges covering the underlying sequence,
    /// annotated with the values in both maps matching each range.
    ///
    /// The sequence of ranges is guaranteed to be sorted, gap-less and ranging
    /// over the entire underlying sequence.
    pub fn zip<'a, U>(
        &'a self,
        other: &'a RangeMap<U>,
    ) -> impl Iterator<Item = (Range<usize>, Option<&'a T>, Option<&'a U>)> {
        zip_range_iterators(self.iter(), other.iter())
    }

    /// Iterate over the contents of the map
    pub fn iter(&self) -> impl Iterator<Item = (Range<usize>, &T)> {
        self.ranges
            .iter()
            .map(|(range, value)| (range.clone(), value))
    }
}

/// Compute an iterator of ranges by joining the two supplied iterators
/// on the ranges that they produce.
///
/// The two iterators are assumed to enumerate disjoint ranges in increasing
/// order, and the resulting iterator is guaranteed to do so as well.
/// It is also gap-less and ranges over the union over all ranges seen in both
/// iterators.
pub fn zip_range_iterators<T: Clone, U: Clone>(
    iter1: impl Iterator<Item = (Range<usize>, T)>,
    iter2: impl Iterator<Item = (Range<usize>, U)>,
) -> impl Iterator<Item = (Range<usize>, Option<T>, Option<U>)> {
    ZipIterator {
        first: iter1.peekable(),
        second: iter2.peekable(),
        next_range_start: 0,
    }
}

/// Internal implementation of [`zip_range_iterators`]
struct ZipIterator<T, U, IterT, IterU>
where
    IterT: Iterator<Item = (Range<usize>, T)>,
    IterU: Iterator<Item = (Range<usize>, U)>,
{
    first: Peekable<IterT>,
    second: Peekable<IterU>,
    /// The start index of the next range to emit
    next_range_start: usize,
}

impl<T, U, IterT, IterU> Iterator for ZipIterator<T, U, IterT, IterU>
where
    T: Clone,
    U: Clone,
    IterT: Iterator<Item = (Range<usize>, T)>,
    IterU: Iterator<Item = (Range<usize>, U)>,
{
    type Item = (Range<usize>, Option<T>, Option<U>);

    fn next(&mut self) -> Option<Self::Item> {
        let range_start = self.next_range_start;

        // Consume all ranges which end before the start of the current range
        while let Some((range_left, _)) = self.first.peek() {
            if range_left.end <= range_start {
                self.first.next();
            } else {
                break;
            }
        }
        while let Some((range_right, _)) = self.second.peek() {
            if range_right.end <= range_start {
                self.second.next();
            } else {
                break;
            }
        }

        let (range_end, result_left, result_right) = match (self.first.peek(), self.second.peek()) {
            (None, None) => return None,
            (None, Some((range, _))) | (Some((range, _)), None) if range_start < range.start => {
                (range.start, None, None)
            }
            (None, Some((range, value))) => (range.end, None, Some(value)),
            (Some((range, value)), None) => (range.end, Some(value), None),
            (Some((range_left, value_left)), Some((range_right, value_right))) => {
                let min_range_start = min(range_left.start, range_right.start);
                if range_start < min_range_start {
                    (min_range_start, None, None)
                } else if range_start < range_left.start {
                    if range_left.start < range_right.end {
                        (range_left.start, None, Some(value_right))
                    } else {
                        (range_right.end, None, Some(value_right))
                    }
                } else if range_start < range_right.start {
                    if range_right.start < range_left.end {
                        (range_right.start, Some(value_left), None)
                    } else {
                        (range_left.end, Some(value_left), None)
                    }
                } else {
                    // both ranges start earlier than range_start
                    (
                        min(range_left.end, range_right.end),
                        Some(value_left),
                        Some(value_right),
                    )
                }
            }
        };
        self.next_range_start = range_end;
        Some((
            range_start..range_end,
            result_left.cloned(),
            result_right.cloned(),
        ))
    }
}

impl<T> FromIterator<(Range<usize>, T)> for RangeMap<T> {
    fn from_iter<I: IntoIterator<Item = (Range<usize>, T)>>(iter: I) -> Self {
        Self::new(iter)
    }
}

#[cfg(test)]
mod tests {

    use super::*;

    #[test]
    #[should_panic]
    fn test_unsorted_ranges() {
        RangeMap::new(vec![(3..4, "foo"), (2..3, "bar")]);
    }

    #[test]
    fn test_get() {
        let range_map = RangeMap::new(vec![(1..3, "a"), (3..3, "huh"), (3..4, "b"), (6..8, "c")]);
        assert_eq!(range_map.get(0), None);
        assert_eq!(range_map.get(1).unwrap(), &(1..3, "a"));
        assert_eq!(range_map.get(2).unwrap(), &(1..3, "a"));
        assert_eq!(range_map.get(3).unwrap(), &(3..4, "b"));
        assert_eq!(range_map.get(4), None);
        assert_eq!(range_map.get(5), None);
        assert_eq!(range_map.get(6).unwrap(), &(6..8, "c"));
        assert_eq!(range_map.get(7).unwrap(), &(6..8, "c"));
        assert_eq!(range_map.get(8), None);
        assert_eq!(range_map.get(9), None);
    }

    #[test]
    fn test_zip() {
        let left = RangeMap::new(vec![
            (1..2, "a"),
            (4..6, "b"),
            (7..8, "c"),
            (8..10, "d"),
            (11..12, "e"),
        ]);
        let right = RangeMap::new(vec![(3..4, "A"), (5..9, "B"), (11..12, "C")]);

        let zipped: Vec<_> = left
            .zip(&right)
            .map(|(range, a, b)| (range, a.copied(), b.copied()))
            .collect();

        let expected = vec![
            (0..1, None, None),
            (1..2, Some("a"), None),
            (2..3, None, None),
            (3..4, None, Some("A")),
            (4..5, Some("b"), None),
            (5..6, Some("b"), Some("B")),
            (6..7, None, Some("B")),
            (7..8, Some("c"), Some("B")),
            (8..9, Some("d"), Some("B")),
            (9..10, Some("d"), None),
            (10..11, None, None),
            (11..12, Some("e"), Some("C")),
        ];

        assert_eq!(zipped, expected);
    }

    #[test]
    fn test_zip_with_left_trailing_disjoint_element() {
        let left = RangeMap::new(vec![(1..3, "a"), (7..8, "b")]);
        let right = RangeMap::new(vec![(2..4, "A")]);

        let zipped: Vec<_> = left
            .zip(&right)
            .map(|(range, a, b)| (range, a.copied(), b.copied()))
            .collect();

        let expected = vec![
            (0..1, None, None),
            (1..2, Some("a"), None),
            (2..3, Some("a"), Some("A")),
            (3..4, None, Some("A")),
            (4..7, None, None),
            (7..8, Some("b"), None),
        ];

        assert_eq!(zipped, expected);
    }

    #[test]
    fn test_zip_with_right_trailing_disjoint_element() {
        let left = RangeMap::new(vec![(2..4, "A")]);
        let right = RangeMap::new(vec![(1..3, "a"), (7..8, "b")]);

        let zipped: Vec<_> = left
            .zip(&right)
            .map(|(range, a, b)| (range, a.copied(), b.copied()))
            .collect();

        let expected = vec![
            (0..1, None, None),
            (1..2, None, Some("a")),
            (2..3, Some("A"), Some("a")),
            (3..4, Some("A"), None),
            (4..7, None, None),
            (7..8, None, Some("b")),
        ];

        assert_eq!(zipped, expected);
    }
}
