"""
Defines the UserQueryCommandCards class, a child of the UserResponseCollector.UserQueryCommand class. It is
a concrete UserQUeryCommand implementation for turning an input string like 'AS 2H KC 10D' into a list of
HandsDecksCards.Card objects.

Exported Classes:
    UserQueryCommandCards - Concrete UserQueryCommand class that knows how to convert a string
                            of text like 'AS 2H KC 10D' into a list of Card objects.     

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    None
 """


# Standard imports

# Local imports
from HandsDecksCards.card import Card
from UserResponseCollector.UserQueryCommand import UserQueryCommand


class UserQueryCommandCards(UserQueryCommand):
    """
    Following the Command design pattern, this is the concrete UserQueryCommand class that knows how to convert a string
    of text like 'AS 2H KC 10D' into a list of Card objects.
    """
    def __init__(self, receiver=None, query_preface = ''):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        """
        UserQueryCommand.__init__(self, receiver, query_preface)

    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for a string of text like 'AS 2H KC 10D' that
        can be processed into a list of Card objects.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, giving the user examples of an acceptable response        
        prompt_text += '(examples AS KH QD JC 10S 9H 8D ... 2C): '
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a list of Card objects.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (list of Card objects, Error message), as Tuple ([Card objects], string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be ([Card objects], '')
        """
        # Process the response from the receiver/user into a list of Card objects.
        processed_response = None
        msg = ''
        try:
            processed_response = Card().make_card_list_from_str(raw_response)
        except:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a valid list of cards. Please try again."  
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate the processed response (list of Card objects) returned from _doProcessRawResponse(...).
        No Validation is required for this UserQueryCommand, so always return (True, '')
        :parameter processed_response: The returned value from _doProcessRawResponse(...), [Card objects]
        :return: Tuple (True, ''), as Tuple (boolean, string)
        """
        return (True, '')
