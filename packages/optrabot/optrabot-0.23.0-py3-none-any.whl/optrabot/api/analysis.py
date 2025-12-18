"""
Analysis API Endpoints

This module provides API endpoints for trade analysis and performance metrics.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

import pytz
from fastapi import APIRouter, Query
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import or_, select

from optrabot.database import SessionLocal
from optrabot.models import Trade as TradeModel
from optrabot.tradestatus import TradeStatus

router = APIRouter(prefix='/api')


class AnalysisTimeRange(str, Enum):
    """Time range filter options for analysis"""
    TODAY = 'today'
    YESTERDAY = 'yesterday'
    THIS_WEEK = 'this_week'
    LAST_WEEK = 'last_week'
    THIS_MONTH = 'this_month'
    LAST_MONTH = 'last_month'
    THIS_YEAR = 'this_year'
    CUSTOM = 'custom'


class AnalysisTrade(BaseModel):
    """Trade information for analysis"""
    id: int
    strategy: str
    template_name: str
    trade_group: Optional[str]
    symbol: str
    status: str
    realized_pnl: Optional[float]
    fees: Optional[float]
    commission: Optional[float]
    entry_time: Optional[str]
    close_time: Optional[str]
    amount: int


class AnalysisData(BaseModel):
    """Analysis data response"""
    trades: List[AnalysisTrade]
    start_date: Optional[str]
    end_date: Optional[str]


def _get_analysis_time_range(
    time_range: AnalysisTimeRange,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None
) -> tuple[Optional[datetime], Optional[datetime]]:
    """
    Get the start and end datetime for the given time range filter.
    Returns (start_date, end_date) tuple.
    """
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    if time_range == AnalysisTimeRange.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
        
    elif time_range == AnalysisTimeRange.YESTERDAY:
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif time_range == AnalysisTimeRange.THIS_WEEK:
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
        
    elif time_range == AnalysisTimeRange.LAST_WEEK:
        # Previous week (Monday to Sunday)
        days_since_monday = now.weekday()
        this_week_start = now - timedelta(days=days_since_monday)
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)
        start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = last_week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif time_range == AnalysisTimeRange.THIS_MONTH:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
        
    elif time_range == AnalysisTimeRange.LAST_MONTH:
        # First day of current month
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of previous month
        last_of_prev_month = first_of_month - timedelta(days=1)
        # First day of previous month
        first_of_prev_month = last_of_prev_month.replace(day=1)
        start = first_of_prev_month
        end = last_of_prev_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif time_range == AnalysisTimeRange.THIS_YEAR:
        # First day of current year (January 1st)
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
        
    elif time_range == AnalysisTimeRange.CUSTOM:
        # Parse custom dates
        start = None
        end = None
        if custom_start:
            try:
                start = datetime.fromisoformat(custom_start)
                if start.tzinfo is None:
                    start = tz.localize(start)
                # Ensure start is at beginning of day
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                logger.warning(f'Invalid custom start date: {custom_start}')
        if custom_end:
            try:
                end = datetime.fromisoformat(custom_end)
                if end.tzinfo is None:
                    end = tz.localize(end)
                # Ensure end is at end of day (23:59:59.999999)
                end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                logger.warning(f'Invalid custom end date: {custom_end}')
    else:
        start = None
        end = None
    
    return start, end


@router.get('/analysis', response_model=AnalysisData)
async def get_analysis_data(
    time_range: AnalysisTimeRange = Query(AnalysisTimeRange.THIS_WEEK, description='Time range filter'),
    strategy: Optional[str] = Query(None, description='Filter by strategy name'),
    start_date: Optional[str] = Query(None, description='Custom start date (ISO format)'),
    end_date: Optional[str] = Query(None, description='Custom end date (ISO format)'),
    group_by_trade_group: bool = Query(False, description='Group trades by trade group')
) -> AnalysisData:
    """
    Get trade data for analysis.
    
    Returns closed trades within the specified time range with P&L data.
    """
    import optrabot.config as optrabotcfg

    # Get time range boundaries
    range_start, range_end = _get_analysis_time_range(time_range, start_date, end_date)
    logger.debug(f'Analysis request: time_range={time_range}, range_start={range_start}, range_end={range_end}')
    
    # Convert to UTC for database comparison (DB stores naive UTC timestamps)
    range_start_utc = range_start.astimezone(pytz.UTC).replace(tzinfo=None) if range_start else None
    range_end_utc = range_end.astimezone(pytz.UTC).replace(tzinfo=None) if range_end else None
    logger.debug(f'UTC range: start={range_start_utc}, end={range_end_utc}')
    
    # Get all templates for looking up template_group and strategy
    config: optrabotcfg.Config = optrabotcfg.appConfig
    all_templates = config.getTemplates() if config else []
    template_map = {t.name: t for t in all_templates}
    
    with SessionLocal() as session:
        # First, let's check what trades exist
        all_trades_query = select(TradeModel)
        all_trades = session.scalars(all_trades_query).all()
        logger.debug(f'Total trades in database: {len(all_trades)}')
        for t in all_trades[-5:]:  # Log last 5 trades
            logger.debug(f'  Trade {t.id}: status={t.status}, closeDate={t.closeDate}, openDate={t.openDate}')
        
        # Build query for closed/expired trades
        query = select(TradeModel).where(
            or_(
                TradeModel.status == TradeStatus.CLOSED,
                TradeModel.status == TradeStatus.EXPIRED
            )
        )
        
        # Apply time range filter
        # Use closeDate if available, otherwise fall back to openDate (for EXPIRED trades without closeDate)
        from sqlalchemy import func
        effective_date = func.coalesce(TradeModel.closeDate, TradeModel.openDate)
        
        if range_start_utc:
            query = query.where(effective_date >= range_start_utc)
        if range_end_utc:
            query = query.where(effective_date <= range_end_utc)
        
        # Order by effective date (closeDate or openDate)
        query = query.order_by(effective_date.asc())
        
        trades = session.scalars(query).all()
        logger.debug(f'Found {len(trades)} closed/expired trades in time range')
        
        result_trades: List[AnalysisTrade] = []
        
        for trade in trades:
            # Get template info for strategy name
            template = template_map.get(trade.template_name)
            strategy_name = template.strategy if template else (trade.strategy or trade.template_name)
            
            # Filter by strategy if specified
            if strategy and strategy_name != strategy:
                continue
            
            # Calculate fees and commission from transactions
            total_fees = 0.0
            total_commission = 0.0
            trade_amount = 0
            for tx in trade.transactions:
                if tx.commission:
                    total_commission += tx.commission
                if tx.fee:
                    total_fees += tx.fee
                if tx.contracts:
                    trade_amount = max(trade_amount, tx.contracts)
            
            result_trades.append(AnalysisTrade(
                id=trade.id,
                strategy=strategy_name,
                template_name=trade.template_name or '',
                trade_group=trade.trade_group_id,
                symbol=trade.symbol,
                status=trade.status,
                realized_pnl=round(trade.realizedPNL, 2) if trade.realizedPNL is not None else None,
                fees=round(total_fees, 2) if total_fees else None,
                commission=round(total_commission, 2) if total_commission else None,
                entry_time=trade.openDate.isoformat() if trade.openDate else None,
                # Use closeDate if available, otherwise fall back to openDate (for EXPIRED trades)
                close_time=(trade.closeDate or trade.openDate).isoformat() if (trade.closeDate or trade.openDate) else None,
                amount=trade_amount or 1,
            ))
        
        # If group_by_trade_group is True, aggregate trades by trade group
        if group_by_trade_group:
            grouped: dict[str, AnalysisTrade] = {}
            ungrouped: List[AnalysisTrade] = []
            
            for trade in result_trades:
                if trade.trade_group:
                    key = trade.trade_group
                    if key not in grouped:
                        grouped[key] = AnalysisTrade(
                            id=trade.id,  # Use first trade's ID
                            strategy=trade.strategy,
                            template_name=trade.template_name,
                            trade_group=trade.trade_group,
                            symbol=trade.symbol,
                            status=trade.status,
                            realized_pnl=trade.realized_pnl or 0,
                            fees=trade.fees or 0,
                            commission=trade.commission or 0,
                            entry_time=trade.entry_time,
                            close_time=trade.close_time,
                            amount=trade.amount,
                        )
                    else:
                        # Aggregate values
                        existing = grouped[key]
                        grouped[key] = AnalysisTrade(
                            id=existing.id,
                            strategy=existing.strategy,
                            template_name=existing.template_name,
                            trade_group=existing.trade_group,
                            symbol=existing.symbol,
                            status=existing.status,
                            realized_pnl=(existing.realized_pnl or 0) + (trade.realized_pnl or 0),
                            fees=(existing.fees or 0) + (trade.fees or 0),
                            commission=(existing.commission or 0) + (trade.commission or 0),
                            entry_time=existing.entry_time,  # Keep first entry time
                            close_time=trade.close_time,  # Use last close time
                            amount=existing.amount + trade.amount,
                        )
                else:
                    ungrouped.append(trade)
            
            result_trades = list(grouped.values()) + ungrouped
            # Re-sort by close time
            result_trades.sort(key=lambda t: t.close_time or '')
        
        return AnalysisData(
            trades=result_trades,
            start_date=range_start.isoformat() if range_start else None,
            end_date=range_end.isoformat() if range_end else None,
        )
