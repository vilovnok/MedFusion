import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { MatDialog } from '@angular/material/dialog';
import { DialogComponent } from '../dialog/dialog.component';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  @ViewChild('chatbox') private chatbox!: ElementRef;

  constructor(private service: ChatService, private dialog: MatDialog) { }

  istyping: boolean = false;
  isPlaye: boolean = false;

  ngOnInit(): void {
    this.checkToken();
    const lastQueries = this.getLastQueryResponses();
    console.log('Последние три запрос-ответ:', lastQueries);

    // lastQueries.forEach((queryResponse, index) => {
    //   this.addMessage('human', queryResponse.human);
    //   this.addMessage('bot', queryResponse.bot);
    // });
  }

  input_text: string = '';
  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }


  messages = [
    {
      role: 'bot',
      text: 'Hello! What are you interested in about the med. domain?',
    },
  ];

  addMessage(role: string, text: string) {
    this.messages.push({ role: role, text: text });
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    this.chatbox.nativeElement.scrollTop = this.chatbox.nativeElement.scrollHeight;
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  async generate() {

    if (!this.input_text.trim()) {
      this.input_text = '';
      return;
    }

    const role = 'human';
    const content_h = this.input_text;
    this.addMessage(role, content_h)
  
    this.input_text = '';
    await this.sleep(2000);
    this.istyping = true;

    const reqBody = {
      "api_key": this.service.getFromLS('api_key'), 
      "content": content_h 
    }

    this.service.handle_post_requests(reqBody, 'agent/retrieve-data').subscribe(async response => {

      await this.sleep(2000);
      this.istyping = false;

      const role = 'bot'
      const content_b = response['text']
      this.addMessage(role, content_b);
      this.saveQueryResponse(content_h, content_b);

    }, async error => {
      await this.sleep(2000);
      const role = 'bot';
      const text = 'Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.'
      this.addMessage(role, text);

      this.istyping = false;
      this.isPlaye = false;
      this.service.rmFromLS('api_key');
    });
    this.input_text = '';
  }

  showDialog() {
    const dialogRef = this.dialog.open(DialogComponent, {
      width: '300px',
      height: '360px',
      data: {}
    });

    dialogRef.afterClosed().subscribe((api_key: string) => {
      if (!api_key.trim()) {
        api_key = '';
        return;
      }
      
      if (api_key) {
        const reqBody = { 
          "api_key": api_key 
        }

        this.service.handle_post_requests(reqBody, 'agent/healthcheck').subscribe(async response => {
          if (response['status'] == 'success') this.isPlaye = true;
          console.log('ok');
          this.service.saveToLS('api_key',api_key);
        }, 
          error => {
            this.service.rmFromLS('api_key');
            this.isPlaye = false;
          }
        );      
      } else {
        this.service.rmFromLS('api_key');
        this.isPlaye = false;
      }
    });
  }


  private saveQueryResponse(userText: string, aiResponse: string): void {
    let queryResponses = JSON.parse(localStorage.getItem('queryResponses') || '[]');  
    queryResponses.unshift({ human: userText, ai: aiResponse });  
    if (queryResponses.length > 3) {
      queryResponses.pop();
    }  
    localStorage.setItem('queryResponses', JSON.stringify(queryResponses));
  }
  
  private getLastQueryResponses(): { human: string, bot: string }[] {
    return JSON.parse(localStorage.getItem('queryResponses') || '[]');
  }

  checkToken() {
    if (!this.service.getFromLS('api_key')){
      this.showDialog();      
    }else{
      this.isPlaye=true;
    }
  }
}
