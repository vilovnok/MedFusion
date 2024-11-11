import { Component, OnInit } from '@angular/core';
import { UserService } from '../services/user.service';
import { FormBuilder } from '@angular/forms';
import { MessageModel } from '../models/message';

@Component({
  selector: 'app-main',

  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss']
})
export class MainComponent implements OnInit {

  prompt: string = '';
  messages: MessageModel[] = [];
  istyping: boolean = false;
  isPlaying: boolean = false;

  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }

  constructor(private service: UserService, private fb: FormBuilder) { }

  ngOnInit(): void { }


  async sendMessage() {
    if (!this.prompt.trim() || this.isPlaying) {
      this.prompt='';
      return;
    }

    this.messages.push({ 'text': this.prompt, 'type': 'human' })
    
    const promptToSend = this.prompt;
    
    this.isPlaying = true;
    
    this.prompt = '';
    
    await this.sleep(2000);
    
    this.istyping = true;
    
    if (promptToSend) {
      const data = this.fb.group({ text: promptToSend });

      const reqBody = {
        "history": [
          {
            "role": "user",
            "content": promptToSend
          }
        ]
      }

      this.service.handle_post_requests(reqBody, 'get_answer').subscribe(response => {
      
        this.istyping = false;
        this.isPlaying = false;
        this.messages.push({ 'text': response['answer'], 'type': 'bot' })

      }, async (err) => {
      
        await this.sleep(2000);
        this.istyping = false;
        this.messages.push({ 'text': "Извините, мы позже вернемся к Вашему вопросу.", 'type': 'bot' })
        console.error('Error sending message: ', err);
        this.isPlaying = false;
      
      });
    }

  }

  async checkTaskStatus(task_id: string) {
    await this.sleep(5000)
    this.service.handle_get_requests(task_id, 'task').subscribe(response => {
      this.istyping = false;
      this.messages.push({ 'text': response['result'], 'type': 'bot' })
      this.isPlaying = false;
    });
  }
}



