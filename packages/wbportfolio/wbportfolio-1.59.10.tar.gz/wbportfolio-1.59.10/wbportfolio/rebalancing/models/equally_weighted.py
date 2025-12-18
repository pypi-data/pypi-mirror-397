from decimal import Decimal

from wbfdm.models import Instrument

from wbportfolio.pms.typing import Portfolio, Position
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Equally Weighted Rebalancing")
class EquallyWeightedRebalancing(AbstractRebalancingModel):
    def __init__(self, *args, **kwargs):
        super(EquallyWeightedRebalancing, self).__init__(*args, **kwargs)
        if not self.effective_portfolio:
            self.effective_portfolio = self.portfolio._build_dto(self.trade_date)
        self.instruments = self._get_instruments(**kwargs)
        self.prices, self.returns_df = Instrument.objects.filter(id__in=self.instruments).get_returns_df(
            from_date=self.last_effective_date, to_date=self.trade_date, use_dl=True
        )
        try:
            self.prices = self.prices[self.trade_date]
        except KeyError:
            self.prices = {}
        try:
            self.returns_df = self.returns_df.loc[self.trade_date, :].to_dict()
        except KeyError:
            self.returns_df = {}

    def _get_instruments(self, **kwargs):
        return list(
            map(
                lambda pp: pp.underlying_instrument,
                filter(lambda p: not p.is_cash, self.effective_portfolio.positions),
            )
        )

    def is_valid(self) -> bool:
        return len(self.instruments) > 0 and self.prices

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        instrument_count = len(self.instruments)
        for underlying_instrument in self.instruments:
            positions.append(
                Position(
                    date=self.trade_date,
                    asset_valuation_date=self.trade_date,
                    underlying_instrument=underlying_instrument,
                    weighting=Decimal(1 / instrument_count),
                    price=self.prices.get(underlying_instrument, None),
                    daily_return=self.returns_df.get(underlying_instrument, Decimal("0")),
                )
            )
        return Portfolio(positions)
