import random
from datetime import datetime
from objects.enumerations import * 
from objects.models import *
from objects.orm_model import *

class TicketSlotFactory():
    def __init__(self):
        super().__init__()
    
    def createTicketSlot(self, slotName: str, slotDescription: str, \
                            startTime: datetime, \
                            endTime: datetime, \
                            slotType: TicketSlot, \
                            genre: Genre) -> TicketSlot:
        """   
            arguments: Details of a ticket slot
            return_type: TicketSlot Object
            description: Validates and saves a new TicketSlot
        """
        ticketSlot = TicketSlotORM(slotId = str(random.randint(1,1000000)), \
            slotName = slotName ,\
            slotDescription = slotDescription, \
            startTime = startTime, \
            endTime = endTime, \
            slotType = slotType.value, \
                genre = genre.value, availTickets = 20)
        ticketSlot.save()
        return TicketSlot.from_orm(ticketSlot)


class TicketFactory():
    def __init__(self):
        super().__init__()
    
    def _createTicket(self, userId: str ,ticketSlot: TicketSlot) -> Ticket:
        ticket = TicketORM(ticketId = "TKT" + str(random.randint(1,1000000)),\
                            userId = userId ,\
                            ticketSlotId = ticketSlot.slotId,\
                            ticketStatus = TicketStatus.Booked.value)
        if(ticket.save()):
            ticketSlot.update(actions=[TicketSlotORM.availTickets.set(TicketSlotORM.availTickets - 1)])
            return Ticket.from_orm(ticket)
        return False

    def _rollbackTicket(self, bookedTicket, ticketSlot):
        if(ticketSlot.update(actions=[TicketSlotORM.availTickets.set(TicketSlotORM.availTickets + 1)])):
            bookedTicket.delete()
            return True
        return False

    def cancelTicket(self, bookedTicket, ticketSlot):
        if(ticketSlot.update(actions=[TicketSlotORM.availTickets.set(TicketSlotORM.availTickets + 1)])):
            bookedTicket.update(actions=[TicketORM.ticketStatus.set(TicketStatus.Canceled.value)])
            return Ticket.from_orm(bookedTicket)
        return False


    def createTickets(self, userId: str, ticketSlot: TicketSlot, numTickets: int = 1):
        bookedTickets = []
        try:
            for t in range(numTickets):
                bookedTickets.append(self._createTicket(userId, ticketSlot))
                # Test Case - Handle case when only some tickets were booked (rollback transaction)
        except:
            for bookedTicket in bookedTickets:
                self._rollbackTicket(bookedTicket, ticketSlot)
        return bookedTickets


class UserFactory():
    def __init__(self):
        super().__init__()
    
    def __createUser(self, phoneNumber: str, userName: str) -> User:
        user = UserORM(userId = "U" + str(random.randint(1,1000000)),\
                            userName = userName ,\
                            phoneNumber = phoneNumber)
        try:
            user.save()
            return User.from_orm(user)
        except:
            return False

    def resolveUser(self, userName: str, phoneNumber: str):
        users = UserORM.scan((UserORM.userName == userName) & (UserORM.phoneNumber == phoneNumber))
        for user in users:
            return user
        return False

    def resolveOrCreateUser(self, userName: str, phoneNumber: str) -> User:
        resolvedUser = self.resolveUser(userName, phoneNumber)
        if(resolvedUser):
            return User.from_orm(resolvedUser)

        user = UserORM(userId = "U" + str(random.randint(1,1000000)),\
                            userName = userName ,\
                            phoneNumber = phoneNumber)
        user.save()
        return User.from_orm(user)
    

