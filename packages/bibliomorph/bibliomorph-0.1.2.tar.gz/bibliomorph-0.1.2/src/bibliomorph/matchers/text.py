import numpy as np
from loguru import logger
from rapidfuzz import fuzz
from scipy.optimize import linear_sum_assignment

from .matcher import BaseMatcher


class TextSimilarityMatcher(BaseMatcher):

    threshold: float = 1

    def match(self, domains, ranges):
        domain_ids = [self.domain_id(item) for item in domains]
        range_ids = [self.range_id(item) for item in ranges]
        domain_values = [self.domain_value(item) for item in domains]
        range_values = [self.range_value(item) for item in ranges]

        costs = []
        for domain_value in domain_values:
            costs.append([])
            for range_value in range_values:
                costs[-1].append(100 - fuzz.ratio(range_value, domain_value))
        costs = np.array(costs)

        # Run Hungarian algorithm to find best overall match
        _, col_ind = linear_sum_assignment(costs)

        final_matches = {}
        for index, domain_value in enumerate(domain_values):
            range_index = col_ind[index]
            cost = costs[index, col_ind[index]]
            if cost > self.threshold:
                logger.debug(
                    f"Couldn't find a good match for '{domain_value}'. Skipping."
                )
                print(range_values[range_index])
                print(cost)
            else:
                final_matches[domain_ids[index]] = (
                    range_ids[range_index],
                    range_values[range_index],
                    float(cost),
                )
        return final_matches
