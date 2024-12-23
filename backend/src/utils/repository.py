from abc import ABC, abstractmethod
from ..db.db import AsyncSession
from sqlalchemy import ColumnExpressionArgument, select, insert, update, delete

class AbstractRepository(ABC):

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError
    
    @abstractmethod
    async def get_all_where(self):
        raise NotImplementedError
    
    @abstractmethod
    async def get_one(self):
        raise NotImplementedError
    
    @abstractmethod
    async def add_one(self):
        raise NotImplementedError
    
    @abstractmethod
    async def update(self):
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self):
        raise NotImplementedError
    
    @abstractmethod
    async def join(self):
        raise NotImplementedError
    
class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__ (self, session: AsyncSession):
        self.session = session

    async def get_all(self, n_tab, **filter_by):
        stmt = select(self.model[n_tab]).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]
        return res
    
    async def get_all_where(self, where: ColumnExpressionArgument[bool], limit: int = None):
        stmt = select(self.model[0]).where(*where).limit(limit)
        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]
        return res
    
    async def get_one(self, n_tab: int, full_model: bool = False, **filter_by):
        try:
            stmt = select(self.model[n_tab]).filter_by(**filter_by).limit(1)
            res = await self.session.execute(stmt)
            res = res.scalar_one()
            if not full_model:        
                res = res.to_read_model() 
            return res
        except Exception as err: 
            print(err)
            return None
        
    async def add_one(self, data: dict, n_tab: int):
        try:
            stmt = insert(self.model[n_tab]).values(**data).returning(self.model[n_tab])            
            res_id = await self.session.execute(stmt)            
            return res_id.scalar_one()
        except Exception as err:
            print(err)
            return None
        
    async def update(self, where: ColumnExpressionArgument[bool], values: dict, n_tab:int):
        try:
            stmt = update(self.model[n_tab]).where(*where).values(**values).returning(self.model[n_tab])
            res = await self.session.execute(stmt)
            return res.scalar_one()
        except Exception as e:
            return None
        
    async def delete(self,n_tab:int, **filter_by):
        try:
            stmt = delete(self.model[n_tab]).filter_by(**filter_by)
            await self.session.execute(stmt)
            return True
        except:
            return None
        
    async def join(self, target, onclause = None, where: ColumnExpressionArgument[bool] = [], start: int = 0, limit: int = 50, order_by = None):
        stmt = select(self.model[0], target).join(target, onclause).where(*where).offset(start).limit(limit).order_by(order_by)
        res = await self.session.execute(stmt)
        res = [row for row in res.all()]
        return res
    
    async def find_all_events(self, n_tab:int, percent:int, **filter_by):
        try:
            stmt = select(self.model[n_tab]).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            res = [row[0].to_read_model().fuid_raw for row in res.all()]
            prevent_count = int(len(res) * (percent/100))        
            res = sorted(res)[:prevent_count:]
            return res
        except Exception:
            return None



# test=# INSERT INTO events ("run_number","event_number","type","version","fuid_raw","dsid") VALUES ('280308042','377', 'RAW' ,'t0001' ,'c668f19f-1830-40cc-98e3-ecae651d9f15','3');