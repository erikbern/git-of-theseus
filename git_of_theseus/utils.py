# -*- coding: utf-8 -*-
#
# Copyright 2016 Erik Bernhardsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools, numpy

def generate_n_colors(n):
    vs = numpy.linspace(.4, .9, 6)
    colors = [(.9, .4, .4)]
    def euclidean(a, b):
        return sum((x-y)**2 for x, y in zip(a, b))
    while len(colors) < n:
        new_color = max(itertools.product(vs, vs, vs), key=lambda a: min(euclidean(a, b) for b in colors))
        colors.append(new_color)
    return colors
